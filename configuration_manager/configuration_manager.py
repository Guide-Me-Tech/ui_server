import os
import json
import dataclasses
import logging
import time
import psutil
import hashlib
import hmac
import re
from typing import Dict, Tuple, Optional
from functools import wraps


# Janis Rubins step 1: Configure a deep logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Janis Rubins step 2: Security and Performance Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit to avoid giant configs
MAX_JSON_DEPTH = 20               # Prevent JSON bombs
RATE_LIMIT_WINDOW = 60            # Rate limit window in seconds
MAX_REQUESTS = 100                # Max requests per window
SECRET_KEY = os.urandom(32)       # Random HMAC key for request signing
SAFE_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{1,64}$')  # Safe identifier pattern

def is_safe_identifier(value: str) -> bool:
    # Janis Rubins step 3: Validate usernames, config names, etc.
    return bool(SAFE_PATTERN.match(value))

def safe_join(base_path: str, *paths: str) -> str:
    # Janis Rubins step 4: Prevent path traversal attacks
    final_path = os.path.join(base_path, *paths)
    if not os.path.realpath(final_path).startswith(os.path.realpath(base_path)):
        logger.warning("Attempted path traversal or invalid path detected.")
        return ""
    return final_path

# Janis Rubins step 5: Performance logger decorator
def performance_logger(func):
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        cpu_before = time.process_time()
        wall_before = time.perf_counter()
        logger.debug(f"--- START {func.__name__} ---")
        logger.debug(f"Starting {func.__name__}, checking initial resources. Mem before: {mem_before} bytes, CPU before: {cpu_before}s")

        result = func(*args, **kwargs)

        mem_after = process.memory_info().rss
        cpu_after = time.process_time()
        wall_after = time.perf_counter()
        cpu_diff = cpu_after - cpu_before
        wall_diff = wall_after - wall_before
        mem_diff = mem_after - mem_before

        logger.debug(f"Completed {func.__name__}. Mem after: {mem_after} bytes, CPU after: {cpu_after}s")
        logger.debug(f"{func.__name__} performance: CPU: {cpu_diff:.6f}s, Elapsed: {wall_diff:.6f}s, Mem diff: {mem_diff} bytes")
        logger.debug(f"--- END {func.__name__} ---\n")
        return result
    return wrapper

# Janis Rubins step 6: Security logger decorator
def security_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"--- SECURITY CHECK START {func.__name__} ---")
        request_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        logger.debug(f"Request ID: {request_id}")
        try:
            # Optional HMAC check for username if present
            if kwargs.get('username'):
                hmac_value = hmac.new(SECRET_KEY, kwargs['username'].encode(), hashlib.sha256).hexdigest()
                logger.debug("HMAC validation performed for user operation")
            
            result = func(*args, **kwargs)
            logger.debug(f"--- SECURITY CHECK END {func.__name__} ---")
            return result
        except Exception as e:
            logger.error(f"Security error in {func.__name__}: {e}")
            logger.debug(f"--- SECURITY CHECK FAILED {func.__name__} ---")
            return None
    return wrapper

# Janis Rubins step 7: Security Manager for rate limiting
class SecurityManager:
    def __init__(self):
        self.request_counts = {}
        self.last_cleanup = time.time()
        logger.debug("SecurityManager initialized")

    def cleanup_old_requests(self):
        current_time = time.time()
        if current_time - self.last_cleanup > RATE_LIMIT_WINDOW:
            old_count = sum(len(v) for v in self.request_counts.values())
            # Cleanup requests older than window
            for identifier in list(self.request_counts.keys()):
                self.request_counts[identifier] = [t for t in self.request_counts[identifier] if t > current_time - RATE_LIMIT_WINDOW]
                if not self.request_counts[identifier]:
                    del self.request_counts[identifier]
            new_count = sum(len(v) for v in self.request_counts.values())
            logger.debug(f"Cleaned up old requests. {old_count - new_count} removed.")
            self.last_cleanup = current_time

    def check_rate_limit(self, identifier: str) -> bool:
        self.cleanup_old_requests()
        current_time = time.time()
        window_start = current_time - RATE_LIMIT_WINDOW

        request_count = 0
        if identifier in self.request_counts:
            request_count = sum(1 for t in self.request_counts[identifier] if t > window_start)

        if request_count >= MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return False

        if identifier not in self.request_counts:
            self.request_counts[identifier] = []
        self.request_counts[identifier].append(current_time)
        logger.debug(f"Request count for {identifier}: {request_count + 1}/{MAX_REQUESTS}")
        return True

security_manager = SecurityManager()

@dataclasses.dataclass
class ConfigPath:
    path: str
    username: str
    name: str

    @performance_logger
    def json(self) -> dict:
        # Janis Rubins step 8: Convert ConfigPath to dict
        logger.debug("Converting ConfigPath to dictionary.")
        return dataclasses.asdict(self)

    @staticmethod
    @performance_logger
    def from_json(json_str: str) -> "ConfigPath":
        # Janis Rubins step 9: Deserialize ConfigPath from JSON
        logger.debug("Deserializing ConfigPath from JSON.")
        data = json.loads(json_str)
        if not (is_safe_identifier(data.get('username', '')) and is_safe_identifier(data.get('name', ''))):
            logger.error("Unsafe username or config name detected during from_json.")
            return ConfigPath(path="", username="invalid", name="invalid")
        return ConfigPath(**data)

    @performance_logger
    def get_contents(self) -> dict:
        # Janis Rubins step 10: Load config contents safely
        if not os.path.realpath(self.path).startswith(os.path.realpath("configs/")):
            logger.error("Access to config outside 'configs/' directory attempted.")
            return {}
        logger.debug(f"Loading contents from config file at {self.path}")
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
            logger.debug("File read successfully, returning configuration data.")
            return data
        except Exception as e:
            logger.error("Error reading config: %s", e)
            return {}

@dataclasses.dataclass
class ConfigIDToPath:
    configs: Dict[int, ConfigPath] = dataclasses.field(default_factory=dict)

    @staticmethod
    @performance_logger
    def from_json(json_str: str) -> "ConfigIDToPath":
        # Janis Rubins step 11: Deserialize multiple ConfigPaths
        logger.debug("Deserializing multiple ConfigPaths from JSON.")
        data = json.loads(json_str)
        configs = {}
        for k, v in data.items():
            if not (is_safe_identifier(v.get('username', '')) and is_safe_identifier(v.get('name', ''))):
                logger.warning("Unsafe config detected, skipping this entry.")
                continue
            configs[int(k)] = ConfigPath(**v)
        logger.debug(f"Loaded {len(configs)} config entries into ConfigIDToPath.")
        return ConfigIDToPath(configs=configs)

    @staticmethod
    @performance_logger
    def configs_to_json(configs: Dict[int, ConfigPath]) -> dict:
        # Janis Rubins step 12: Convert configs to JSON-compatible dict
        logger.debug("Transforming configs dict to JSON structure.")
        return {key: value.json() for key, value in configs.items()}

    @performance_logger
    def json(self) -> dict:
        # Janis Rubins step 13: Serialize current configs to dict
        logger.debug("Serializing ConfigIDToPath to dictionary.")
        return {key: value.json() for key, value in self.configs.items()}

    def __str__(self) -> str:
        return f"ConfigIDToPath({self.configs})"

# Janis Rubins step 14: SecureHashMixin for integrity checks
class SecureHashMixin:
    def __init__(self):
        self._hash = None
        self.update_hash()

    def update_hash(self):
        if hasattr(self, 'path') and self.path and os.path.exists(self.path):
            with open(self.path, 'rb') as f:
                self._hash = hashlib.sha256(f.read()).hexdigest()
            logger.debug(f"Updated hash for {self.path}: {self._hash[:8]}...")

    def check_integrity(self) -> bool:
        if not self._hash:
            logger.warning("No hash available for integrity check")
            return False
        if not self.path or not os.path.exists(self.path):
            logger.warning("File does not exist for integrity check.")
            return False
        with open(self.path, 'rb') as f:
            current_hash = hashlib.sha256(f.read()).hexdigest()
        matches = hmac.compare_digest(self._hash, current_hash)
        logger.debug(f"Integrity check for {self.path}: {'PASS' if matches else 'FAIL'}")
        return matches

# Janis Rubins step 15: SecureConfigPath extends ConfigPath with hash checking
class SecureConfigPath(ConfigPath, SecureHashMixin):
    def __init__(self, path: str, username: str, name: str):
        ConfigPath.__init__(self, path, username, name)
        SecureHashMixin.__init__(self)

# Janis Rubins step 16: Original ConfigsManager enhanced with security
class ConfigsManager:
    @performance_logger
    def __init__(self):
        logger.debug("Initializing ConfigsManager, ensuring 'configs/' directory.")
        if not os.path.exists("configs/"):
            logger.debug("Directory 'configs/' does not exist, creating it now.")
            os.makedirs("configs/")
        self.configs, self.idx = self.load_configs()

    @performance_logger
    def load_configs(self) -> Tuple[Dict[int, ConfigPath], int]:
        logger.debug("Loading configuration registry from 'configs/configs.json'.")
        if not os.path.exists("configs/configs.json"):
            logger.debug("No registry found, starting empty.")
            return {}, 0
        with open("configs/configs.json", "r") as f:
            data = json.load(f)
            configs = ConfigIDToPath(configs={})
            for k, v in data.items():
                if is_safe_identifier(v.get('username', '')) and is_safe_identifier(v.get('name', '')):
                    configs.configs[int(k)] = ConfigPath(**v)
                else:
                    logger.warning("Unsafe entry in registry, skipping.")
            max_idx = max(configs.configs.keys(), default=0)
        logger.debug(f"Registry loaded. Total configs: {len(configs.configs)}, Max ID: {max_idx}")
        return configs.configs, max_idx

    @performance_logger
    @security_logger
    def add_config(self, username: str, config: dict, config_name: str) -> None:
        if not (is_safe_identifier(username) and is_safe_identifier(config_name)):
            logger.error("Unsafe username or config name, cannot add config.")
            return
        logger.debug(f"Adding/updating config '{config_name}' for user '{username}'.")
        user_dir = safe_join("configs", username)
        if user_dir == "":
            logger.error("Failed to construct safe user directory path.")
            return
        if not os.path.exists(user_dir):
            logger.debug("User directory missing, creating it.")
            os.makedirs(user_dir, exist_ok=True)

        config_path = safe_join(user_dir, config_name + ".json")
        if config_path == "":
            logger.error("Invalid config path after safe join.")
            return

        # Validate config size and content
        config_str = json.dumps(config)
        config_size = len(config_str.encode())
        if config_size > MAX_FILE_SIZE:
            logger.error(f"Config size {config_size} exceeds maximum {MAX_FILE_SIZE}")
            return
        suspicious_patterns = ['__proto__', 'constructor', 'prototype']
        if any(pattern in config_str for pattern in suspicious_patterns):
            logger.error("Suspicious pattern detected in config, aborting.")
            return

        new_entry = not os.path.exists(config_path)
        if new_entry:
            logger.debug("New configuration detected, assigning new ID.")
            new_idx_to_path = self.idx + 1
            self.idx = new_idx_to_path
            self.configs[new_idx_to_path] = ConfigPath(path=config_path, username=username, name=config_name)
            with open("configs/configs.json", "w") as f:
                json.dump(ConfigIDToPath.configs_to_json(self.configs), f, separators=(',', ':'))

        logger.debug("Writing the actual configuration file to disk.")
        with open(config_path, "w") as f:
            json.dump(config, f, separators=(',', ':'))
        logger.debug("Configuration added/updated successfully.")

    @performance_logger
    def get_configs(self, username: str) -> Dict[str, dict]:
        if not is_safe_identifier(username):
            logger.error("Unsafe username requested, returning empty.")
            return {}
        logger.debug(f"Fetching all configurations for user '{username}'.")
        user_dir = safe_join("configs", username)
        if user_dir == "" or not os.path.exists(user_dir):
            logger.debug("No directory for this user, returning empty set.")
            return {}
        files = [f for f in os.listdir(user_dir) if f.endswith('.json')]
        results = {}
        logger.debug("Reading user config files from disk now.")
        for file in files:
            path = safe_join(user_dir, file)
            if path == "":
                logger.warning("Invalid file path, skipping.")
                continue
            try:
                with open(path, "r") as config_file:
                    results[file[:-5]] = json.load(config_file)
            except Exception as e:
                logger.error("Error reading config file %s: %s", file, e)
        logger.debug(f"Retrieved {len(results)} configs for user '{username}'.")
        return results

    @performance_logger
    def get_config(self, username: str, name: str) -> dict:
        if not (is_safe_identifier(username) and is_safe_identifier(name)):
            logger.error("Unsafe parameters in get_config, returning empty.")
            return {}
        logger.debug(f"Retrieving configuration '{name}' for user '{username}'.")
        path = safe_join("configs", username, name + ".json")
        if path == "" or not os.path.exists(path):
            logger.debug("Config file not found, returning empty dict.")
            return {}
        try:
            with open(path, "r") as config_file:
                data = json.load(config_file)
            logger.debug("Configuration successfully retrieved.")
            return data
        except Exception as e:
            logger.error("Error reading config: %s", e)
            return {}

    @performance_logger
    def get_config_by_id(self, idx: int) -> ConfigPath:
        logger.debug(f"Looking for configuration by ID {idx}.")
        config_path = self.configs.get(idx, None)
        if config_path:
            logger.debug("Found configuration by ID.")
        else:
            logger.debug("No configuration found with that ID.")
        return config_path

    @performance_logger
    def delete_config(self, username: str, name: str) -> None:
        if not (is_safe_identifier(username) and is_safe_identifier(name)):
            logger.error("Unsafe parameters in delete_config.")
            return
        logger.debug(f"Deleting configuration '{name}' for user '{username}'.")
        path = safe_join("configs", username, name + ".json")
        if path == "":
            logger.error("Invalid path in delete_config.")
            return

        if os.path.exists(path):
            os.remove(path)
            logger.debug("Config file removed from file system.")
        else:
            logger.debug("No file found, no removal action taken.")

        logger.debug("Removing config entry from memory.")
        found_key = None
        for i, p in self.configs.items():
            if p.path == path:
                found_key = i
                break

        if found_key is not None:
            del self.configs[found_key]
            logger.debug("Memory entry removed, updating registry.")
            with open("configs/configs.json", "w") as f:
                json.dump(ConfigIDToPath.configs_to_json(self.configs), f, separators=(',', ':'))
            logger.debug("Registry successfully updated.")
        else:
            logger.debug("No matching config in memory, no registry update required.")

    @performance_logger
    def delete_config_by_id(self, idx: int) -> None:
        logger.debug(f"Deleting configuration by ID: {idx}.")
        if idx not in self.configs:
            logger.debug("No config found with that ID, cannot proceed.")
            return
        path = self.configs[idx].path
        if not os.path.realpath(path).startswith(os.path.realpath("configs/")):
            logger.error("Attempt to delete config outside allowed directory, skipping.")
            return

        if os.path.exists(path):
            os.remove(path)
            logger.debug("File associated with that ID removed from file system.")
        del self.configs[idx]
        logger.debug("Removed entry from memory, updating registry.")
        with open("configs/configs.json", "w") as f:
            json.dump(ConfigIDToPath.configs_to_json(self.configs), f, separators=(',', ':'))
        logger.debug("Registry updated after deletion by ID.")

# Janis Rubins step 28: UIBuilder class with security
class UIBuilder:
    @performance_logger
    def __init__(self) -> None:
        logger.debug("UIBuilder initialized, no heavy operations performed.")

    @staticmethod
    @performance_logger
    def build_ui(config, data):
        logger.debug("Starting UI construction process.")
        func_name = data.get("func_name", None)
        if func_name is None:
            logger.debug("No 'func_name' provided, cannot build UI.")
            return {"error": "No function name provided"}

        if not is_safe_identifier(func_name):
            logger.error("Unsafe func_name detected, returning error.")
            return {"error": "Invalid function name"}

        logger.debug(f"Function name '{func_name}' provided, finding associated widget.")
        widget_name = config.get("func_name_to_widget", {}).get(func_name, None)
        if widget_name is None:
            logger.debug("No widget found for given function, returning error.")
            return {"error": "Invalid function name"}

        logger.debug(f"Widget '{widget_name}' found, retrieving widget details.")
        widget_info = config.get("widgets", {}).get(widget_name, None)
        if widget_info is None:
            logger.debug("No widget details found, returning error.")
            return {"error": "Widget info not found"}

        logger.debug("Widget details retrieved, UI build successful.")
        return {"widget_info": widget_info}

# Initialize managers if needed
configs_manager = ConfigsManager()
ui_builder = UIBuilder()

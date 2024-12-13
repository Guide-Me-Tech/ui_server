import os
import json
import dataclasses
import logging
import time
import psutil
from typing import Dict, Tuple

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Janis Rubins: Added performance_logger decorator to measure performance (CPU, time, memory)
def performance_logger(func):
    def wrapper(*args, **kwargs):
        # Janis Rubins: Use psutil to track memory before running the function
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        cpu_before = time.process_time()
        wall_before = time.perf_counter()
        logger.debug(f"--- START {func.__name__} ---")
        logger.debug(f"Starting {func.__name__}, checking initial resources. Memory before: {mem_before} bytes, CPU before: {cpu_before}s")

        # Janis Rubins: Execute the actual function
        result = func(*args, **kwargs)

        # Janis Rubins: After execution, measure memory and CPU again to identify resource usage
        mem_after = process.memory_info().rss
        cpu_after = time.process_time()
        wall_after = time.perf_counter()
        cpu_diff = cpu_after - cpu_before
        wall_diff = wall_after - wall_before
        mem_diff = mem_after - mem_before

        logger.debug(f"Completed {func.__name__}. Memory after: {mem_after} bytes, CPU after: {cpu_after}s")
        logger.debug(f"{func.__name__} performance: CPU: {cpu_diff:.6f}s, Elapsed: {wall_diff:.6f}s, Mem diff: {mem_diff} bytes")
        logger.debug(f"--- END {func.__name__} ---\n")
        return result
    return wrapper

@dataclasses.dataclass
class ConfigPath:
    path: str      # Janis Rubins: Holds file path to a specific config file
    username: str  # Janis Rubins: Links config to a username
    name: str      # Janis Rubins: Config identifier name

    @performance_logger
    def json(self) -> dict:
        # Janis Rubins: Converting dataclass to dict directly, simpler and faster
        logger.debug("Converting ConfigPath to dictionary representation.")
        return dataclasses.asdict(self)

    @staticmethod
    @performance_logger
    def from_json(json_str: str) -> "ConfigPath":
        # Janis Rubins: Direct JSON load into a ConfigPath instance
        logger.debug("Deserializing ConfigPath from a JSON string.")
        data = json.loads(json_str)
        logger.debug("JSON parsed, creating ConfigPath instance.")
        return ConfigPath(**data)

    @performance_logger
    def get_contents(self) -> dict:
        # Janis Rubins: Read the config file directly and load as dict
        logger.debug(f"Loading contents from config file at {self.path}")
        with open(self.path, "r") as f:
            data = json.load(f)
        logger.debug("File read successfully, returning configuration data.")
        return data

@dataclasses.dataclass
class ConfigIDToPath:
    configs: Dict[int, ConfigPath] = dataclasses.field(default_factory=dict)  
    # Janis Rubins: Stores multiple ConfigPath objects indexed by int IDs

    @staticmethod
    @performance_logger
    def from_json(json_str: str) -> "ConfigIDToPath":
        # Janis Rubins: Deserialize multiple configs from a JSON string into a dict of ConfigPath
        logger.debug("Deserializing multiple ConfigPaths from JSON.")
        data = json.loads(json_str)
        configs = {int(k): ConfigPath(**v) for k, v in data.items()}
        logger.debug(f"Loaded {len(configs)} config entries into ConfigIDToPath.")
        return ConfigIDToPath(configs=configs)

    @staticmethod
    @performance_logger
    def configs_to_json(configs: Dict[int, ConfigPath]) -> dict:
        # Janis Rubins: Convert all configs to a JSON-ready dict using each ConfigPath's json method
        logger.debug("Transforming configs dict to a JSON-compatible structure.")
        return {key: value.json() for key, value in configs.items()}

    @performance_logger
    def json(self) -> dict:
        # Janis Rubins: Serialize current configs to a dictionary suitable for JSON
        logger.debug("Serializing ConfigIDToPath to a dictionary.")
        return {key: value.json() for key, value in self.configs.items()}

    def __str__(self) -> str:
        return f"ConfigIDToPath({self.configs})"  # Janis Rubins: Simple string representation

class ConfigsManager:
    @performance_logger
    def __init__(self):
        # Janis Rubins: Ensure 'configs' directory exists and load the existing config registry
        logger.debug("Initializing ConfigsManager and ensuring main config directory.")
        if not os.path.exists("configs/"):
            logger.debug("Directory 'configs/' does not exist, creating it now.")
            os.makedirs("configs/")
        self.configs, self.idx = self.load_configs()

    @performance_logger
    def load_configs(self) -> Tuple[Dict[int, ConfigPath], int]:
        # Janis Rubins: Load configurations from the main registry file if present
        logger.debug("Loading configuration registry from 'configs/configs.json'.")
        if not os.path.exists("configs/configs.json"):
            logger.debug("No registry file found, starting with empty set.")
            return {}, 0
        with open("configs/configs.json", "r") as f:
            data = json.load(f)
            # Janis Rubins: Build a dictionary of ConfigPath indexed by int keys
            configs = ConfigIDToPath(configs={int(k): ConfigPath(**v) for k, v in data.items()})
        max_idx = max(configs.configs.keys(), default=0)
        logger.debug(f"Registry loaded. Total configs: {len(configs.configs)}, Max ID: {max_idx}")
        return configs.configs, max_idx

    @performance_logger
    def add_config(self, username: str, config: dict, config_name: str) -> None:
        # Janis Rubins: Add a new config or update existing, also update registry if new
        logger.debug(f"Adding/updating config '{config_name}' for user '{username}'.")
        user_dir = f"configs/{username}"
        if not os.path.exists(user_dir):
            logger.debug("User directory missing, creating it.")
            os.makedirs(user_dir, exist_ok=True)

        config_path = f"{user_dir}/{config_name}.json"
        if not os.path.exists(config_path):
            logger.debug("New configuration detected, assigning new ID and updating main registry.")
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
        # Janis Rubins: Retrieve all configs for a user, loading each file
        logger.debug(f"Fetching all configurations for user '{username}'.")
        user_dir = f"configs/{username}"
        if not os.path.exists(user_dir):
            logger.debug("No directory for this user, returning empty set.")
            return {}
        files = [f for f in os.listdir(user_dir) if f.endswith('.json')]
        results = {}
        logger.debug("Reading user config files from disk now.")
        for file in files:
            path = f"{user_dir}/{file}"
            with open(path, "r") as config_file:
                results[file[:-5]] = json.load(config_file)
        logger.debug(f"Retrieved {len(results)} configs for user '{username}'.")
        return results

    @performance_logger
    def get_config(self, username: str, name: str) -> dict:
        # Janis Rubins: Get a single config by user and name if file exists
        logger.debug(f"Retrieving configuration '{name}' for user '{username}'.")
        path = f"configs/{username}/{name}.json"
        if not os.path.exists(path):
            logger.debug("Config file not found, returning empty dict.")
            return {}
        with open(path, "r") as config_file:
            data = json.load(config_file)
        logger.debug("Configuration successfully retrieved.")
        return data

    @performance_logger
    def get_config_by_id(self, idx: int) -> ConfigPath:
        # Janis Rubins: Retrieve config by integer ID from internal dictionary
        logger.debug(f"Looking for configuration by ID {idx}.")
        config_path = self.configs.get(idx, None)
        if config_path:
            logger.debug("Found configuration by ID.")
        else:
            logger.debug("No configuration found with that ID.")
        return config_path

    @performance_logger
    def delete_config(self, username: str, name: str) -> None:
        # Janis Rubins: Remove config file and update registry if entry is found
        logger.debug(f"Deleting configuration '{name}' for user '{username}'.")
        path = f"configs/{username}/{name}.json"
        if os.path.exists(path):
            os.remove(path)
            logger.debug("Config file removed from file system.")
        else:
            logger.debug("No file found, no removal action taken.")

        logger.debug("Checking and removing config entry from memory.")
        found_key = None
        for idx, p in self.configs.items():
            if p.path == path:
                found_key = idx
                break

        if found_key is not None:
            del self.configs[found_key]
            logger.debug("Memory entry removed, updating registry now.")
            with open("configs/configs.json", "w") as f:
                json.dump(ConfigIDToPath.configs_to_json(self.configs), f, separators=(',', ':'))
            logger.debug("Registry successfully updated.")
        else:
            logger.debug("No matching config in memory, no registry update required.")

    @performance_logger
    def delete_config_by_id(self, idx: int) -> None:
        # Janis Rubins: Delete a config by ID, remove file if exists and update registry
        logger.debug(f"Deleting configuration by ID: {idx}.")
        if idx not in self.configs:
            logger.debug("No config found with that ID, cannot proceed with deletion.")
            return
        path = self.configs[idx].path
        if os.path.exists(path):
            os.remove(path)
            logger.debug("File associated with that ID removed from file system.")
        del self.configs[idx]
        logger.debug("Removed entry from memory, updating registry.")
        with open("configs/configs.json", "w") as f:
            json.dump(ConfigIDToPath.configs_to_json(self.configs), f, separators=(',', ':'))
        logger.debug("Registry updated after deletion by ID.")

class UIBuilder:
    @performance_logger
    def __init__(self) -> None:
        # Janis Rubins: Initialize UIBuilder with minimal overhead
        logger.debug("UIBuilder initialized, no heavy operations performed here.")

    @staticmethod
    @performance_logger
    def build_ui(config, data):
        # Janis Rubins: Use the config and provided data to map function name to a widget
        logger.debug("Starting UI construction process.")
        func_name = data.get("func_name", None)
        if func_name is None:
            logger.debug("No 'func_name' in data, cannot build UI.")
            return {"error": "No function name provided"}

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

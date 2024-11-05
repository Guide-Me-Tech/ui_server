import os
import json
import dataclasses
from typing import Dict


@dataclasses.dataclass
class ConfigPath:
    """
    Represents a configuration path with associated metadata.

    Attributes:
        path (str): The file path to the configuration JSON file.
        username (str): The username associated with the configuration.
        name (str): The name identifier for the configuration.
    """

    path: str
    username: str
    name: str

    def json(self) -> str:
        """
        Serialize the ConfigPath instance to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representation of the ConfigPath instance.
        """
        return dataclasses.asdict(self)

    @staticmethod
    def from_json(json_str: str) -> "ConfigPath":
        """
        Deserialize a JSON string to a ConfigPath instance.

        Args:
            json_str (str): A JSON string representing a ConfigPath instance.

        Returns:
            ConfigPath: An instance of ConfigPath.
        """
        data = json.loads(json_str)
        return ConfigPath(**data)

    def get_contents(self) -> dict:
        """
        Read and return the contents of the configuration file.

        Returns:
            dict: The contents of the JSON configuration file.

        Raises:
            FileNotFoundError: If the file does not exist at the specified path.
        """
        with open(self.path, "r") as f:
            return json.load(f)


@dataclasses.dataclass
class ConfigIDToPath:
    """
    A collection of configurations indexed by integer keys.

    Attributes:
        configs (Dict[int, ConfigPath]): A dictionary mapping integer keys to ConfigPath instances.
    """

    configs: Dict[int, ConfigPath] = dataclasses.field(default_factory=dict)

    @staticmethod
    def from_json(json_str: str) -> "ConfigIDToPath":
        """
        Deserialize a JSON string to a ConfigIDToPath instance.

        Args:
            json_str (str): A JSON string representing a dictionary of configurations.

        Returns:
            ConfigIDToPath: An instance with configs mapped by integer keys.
        """
        data = json.loads(json_str)
        configs = {int(key): ConfigPath(**value) for key, value in data.items()}
        return ConfigIDToPath(configs=configs)

    @staticmethod
    def configs_to_json(configs: Dict[int, ConfigPath]) -> dict:
        """
        Convert configs dictionary to a JSON-compatible dictionary.

        Args:
            configs (Dict[int, ConfigPath]): A dictionary of configurations.

        Returns:
            dict: JSON-compatible dictionary of the configurations.
        """
        return {key: value.json() for key, value in configs.items()}

    def json(self) -> dict:
        """
        Serialize the ConfigIDToPath instance to a JSON-compatible dictionary.

        Returns:
            dict: JSON-compatible dictionary of configs.
        """
        return {key: value.json() for key, value in self.configs.items()}

    def __str__(self) -> str:
        """
        String representation of the ConfigIDToPath instance.

        Returns:
            str: A string representation of the configs dictionary.
        """
        return f"ConfigIDToPath({self.configs})"


class ConfigsManager:
    """
    Manages multiple configurations by reading, adding, retrieving, and deleting them.

    Attributes:
        configs (Dict[int, ConfigPath]): A dictionary of configurations indexed by integer keys.
        idx (int): The highest integer index currently in use in configs.
    """

    def __init__(self):
        """
        Initialize ConfigsManager by loading configurations from 'configs/configs.json'.
        """
        if not os.path.exists("configs/"):
            os.makedirs("configs/")
        self.configs, self.idx = self.load_configs()

    def load_configs(self) -> (Dict[int, ConfigPath], int):
        """
        Load configurations from 'configs/configs.json'.

        Returns:
            Tuple[Dict[int, ConfigPath], int]: A dictionary of configurations and the highest index used.
        """
        with open("configs/configs.json", "r") as f:
            data = f.read()
            configs = ConfigIDToPath.from_json(data)
        return configs.configs, max(configs.configs.keys(), default=0)

    def add_config(self, username: str, config: dict, config_name: str) -> None:
        """
        Add a new configuration to configs and save it in 'configs/configs.json'.

        Args:
            username (str): The username associated with the new configuration.
            config (dict): The JSON data for the configuration.
            config_name (str): The name identifier for the configuration.
        """

        os.makedirs(f"configs/{username}", exist_ok=True)

        if not os.path.exists(f"configs/{username}/{config_name}.json"):
            new_idx_to_path = self.idx + 1
            self.idx = new_idx_to_path
            self.configs[new_idx_to_path] = ConfigPath(
                path=f"configs/{username}/{config_name}.json",
                username=username,
                name=config_name,
            )
            configs = ConfigIDToPath.configs_to_json(self.configs)
            with open("configs/configs.json", "w") as f:
                json.dump(configs, f)

        with open(f"configs/{username}/{config_name}.json", "w") as f:
            json.dump(config, f)

    def get_configs(self, username: str) -> Dict[str, dict]:
        """
        Retrieve all configurations for a specific user.

        Args:
            username (str): The username associated with the configurations.

        Returns:
            Dict[str, dict]: A dictionary of configuration contents.
        """
        files = os.listdir(f"configs/{username}")

        def read_file(path):
            with open(path, "r") as config_file:
                return json.load(config_file)

        return {
            file.replace(".json", ""): read_file(f"configs/{username}/{file}")
            for file in files
        }

    def get_config(self, username: str, name: str) -> dict:
        """
        Retrieve a specific configuration by username and config name.

        Args:
            username (str): The username associated with the configuration.
            name (str): The configuration name.

        Returns:
            dict: The configuration data.
        """
        with open(f"configs/{username}/{name}.json", "r") as config_file:
            return json.load(config_file)

    def get_config_by_id(self, idx: int) -> ConfigPath:
        """
        Retrieve a configuration by its integer ID.

        Args:
            idx (int): The configuration ID.

        Returns:
            ConfigPath: The configuration with the specified ID.
        """
        return self.configs.get(idx, None)

    def delete_config(self, username: str, name: str) -> None:
        """
        Delete a specific configuration by username and config name.

        Args:
            username (str): The username associated with the configuration.
            name (str): The configuration name.
        """
        path = f"configs/{username}/{name}.json"
        os.remove(path)

        for idx, p in self.configs.items():
            if p.path == path:
                del self.configs[idx]
                break

        configs = ConfigIDToPath.configs_to_json(self.configs)
        with open("configs/configs.json", "w") as f:
            json.dump(configs, f)

    def delete_config_by_id(self, idx: int) -> None:
        """
        Delete a configuration by its integer ID.

        Args:
            idx (int): The configuration ID to delete.
        """
        if idx not in self.configs:
            return None
        os.remove(self.configs[idx].path)
        del self.configs[idx]

        configs = ConfigIDToPath.configs_to_json(self.configs)
        with open("configs/configs.json", "w") as f:
            json.dump(configs, f)


class UIBuilder:
    def __init__(self) -> None:
        pass

    @staticmethod
    def build_ui(config, data):
        return ""

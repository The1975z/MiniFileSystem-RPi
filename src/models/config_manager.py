import json
import os
from pathlib import Path
from typing import Dict, List, Optional
class SSHConfig:
    def __init__(self, name: str, host: str, port: int, username: str,
                 password: Optional[str] = None, identity_file: Optional[str] = None,
                 protocol: str = "SFTP"):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.identity_file = identity_file
        self.protocol = protocol

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "identity_file": self.identity_file,
            "protocol": self.protocol
        }

    @staticmethod
    def from_dict(data: Dict) -> 'SSHConfig':
        return SSHConfig(
            name=data.get("name", ""),
            host=data.get("host", ""),
            port=data.get("port", 22),
            username=data.get("username", ""),
            password=data.get("password"),
            identity_file=data.get("identity_file"),
            protocol=data.get("protocol", "SFTP")
        )


class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_dir = Path.home() / ".gui_os"
        self.config_file = self.config_dir / config_file
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_connection(self, config: SSHConfig):
        connections = self.load_all_connections()
        connections[config.name] = config.to_dict()

        with open(self.config_file, 'w') as f:
            json.dump({"connections": connections}, f, indent=2)

    def load_all_connections(self) -> Dict[str, Dict]:
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return data.get("connections", {})
        except:
            return {}

    def get_connection(self, name: str) -> Optional[SSHConfig]:
        connections = self.load_all_connections()
        if name in connections:
            return SSHConfig.from_dict(connections[name])
        return None

    def delete_connection(self, name: str):
        connections = self.load_all_connections()
        if name in connections:
            del connections[name]
            with open(self.config_file, 'w') as f:
                json.dump({"connections": connections}, f, indent=2)

    def get_connection_names(self) -> List[str]:
        return list(self.load_all_connections().keys())

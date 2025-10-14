from typing import Optional, Tuple, Callable
from models.ssh_connection import SSHConnection
from models.config_manager import ConfigManager, SSHConfig
class ConnectionController:
    def __init__(self):
        self.ssh_connection = SSHConnection()
        self.config_manager = ConfigManager()
        self.on_connection_change: Optional[Callable[[bool], None]] = None

    def connect(self, host: str, port: int, username: str,
                password: Optional[str] = None,
                identity_file: Optional[str] = None,
                protocol: str = "SFTP",
                passphrase: Optional[str] = None) -> Tuple[bool, str]:

        success, message = self.ssh_connection.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            identity_file=identity_file,
            passphrase=passphrase
        )

        if self.on_connection_change:
            self.on_connection_change(success)

        return success, message

    def disconnect(self):
        self.ssh_connection.disconnect()
        if self.on_connection_change:
            self.on_connection_change(False)

    def is_connected(self) -> bool:
        return self.ssh_connection.is_connected()

    def get_connection(self) -> SSHConnection:
        return self.ssh_connection

    def save_connection_config(self, name: str, host: str, port: int,
                               username: str, password: Optional[str] = None,
                               identity_file: Optional[str] = None,
                               protocol: str = "SFTP"):
        config = SSHConfig(
            name=name,
            host=host,
            port=port,
            username=username,
            password=password,
            identity_file=identity_file,
            protocol=protocol
        )
        self.config_manager.save_connection(config)

    def load_connection_config(self, name: str) -> Optional[SSHConfig]:
        return self.config_manager.get_connection(name)

    def get_saved_connections(self):
        return self.config_manager.get_connection_names()

    def delete_saved_connection(self, name: str):
        self.config_manager.delete_connection(name)

    def connect_with_config(self, config_name: str) -> Tuple[bool, str]:
        config = self.load_connection_config(config_name)
        if not config:
            return False, "Configuration not found"

        return self.connect(
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password,
            identity_file=config.identity_file,
            protocol=config.protocol
        )

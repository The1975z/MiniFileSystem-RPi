import logging
import os
from datetime import datetime
from pathlib import Path
import traceback
import sys
class AppLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        project_root = Path(__file__).parent.parent
        self.log_dir = project_root / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"app_{timestamp}.log"

        self.logger = logging.getLogger("GUI_OS")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self._initialized = True
        self.info("Application started", "AppLogger.__init__")
        self.info(f"Log file: {log_file}", "AppLogger.__init__")

    def _get_caller_info(self):
        frame = sys._getframe(2)
        return frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name

    def debug(self, message: str, function: str = None):
        if function:
            self.logger.debug(f"[{function}] {message}")
        else:
            self.logger.debug(message)

    def info(self, message: str, function: str = None):
        if function:
            self.logger.info(f"[{function}] {message}")
        else:
            self.logger.info(message)

    def warning(self, message: str, function: str = None):
        if function:
            self.logger.warning(f"[{function}] {message}")
        else:
            self.logger.warning(message)

    def error(self, message: str, function: str = None, exc_info=None):
        if function:
            self.logger.error(f"[{function}] {message}", exc_info=exc_info)
        else:
            self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str, function: str = None, exc_info=None):
        if function:
            self.logger.critical(f"[{function}] {message}", exc_info=exc_info)
        else:
            self.logger.critical(message, exc_info=exc_info)

    def exception(self, message: str, function: str = None):
        tb = traceback.format_exc()
        full_message = f"[{function}] {message}\n{tb}" if function else f"{message}\n{tb}"
        self.logger.error(full_message)

    def log_function_call(self, function_name: str, **kwargs):
        params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.debug(f"Function called with params: {params}", function_name)

    def log_connection_attempt(self, host: str, port: int, username: str, protocol: str):
        self.info(
            f"Connection attempt - Host: {host}, Port: {port}, User: {username}, Protocol: {protocol}",
            "ConnectionController.connect"
        )

    def log_connection_success(self, host: str):
        self.info(f"Successfully connected to {host}", "ConnectionController.connect")

    def log_connection_failure(self, host: str, error: str):
        self.error(f"Failed to connect to {host}: {error}", "ConnectionController.connect")

    def log_file_operation(self, operation: str, path: str, success: bool, error: str = None):
        if success:
            self.info(f"File operation '{operation}' succeeded: {path}", "FileOperations")
        else:
            self.error(f"File operation '{operation}' failed: {path} - {error}", "FileOperations")

    def log_ssh_command(self, command: str, exit_code: int):
        self.info(f"SSH command executed: '{command}' (exit code: {exit_code})", "SSHConnection.execute_command")

    def cleanup_old_logs(self, days: int = 7):
        cutoff = datetime.now().timestamp() - (days * 86400)
        for log_file in self.log_dir.glob("app_*.log"):
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
                self.info(f"Deleted old log file: {log_file.name}", "AppLogger.cleanup_old_logs")


logger = AppLogger()

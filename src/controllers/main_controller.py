from controllers.connection_controller import ConnectionController
from controllers.file_controller import FileController
class MainController:
    def __init__(self):
        self.connection_controller = ConnectionController()
        self.file_controller = FileController(self.connection_controller.get_connection())

        self.connection_controller.on_connection_change = self._on_connection_changed

    def _on_connection_changed(self, connected: bool):
        if connected:
            self.file_controller.initialize()

    def get_connection_controller(self) -> ConnectionController:
        return self.connection_controller

    def get_file_controller(self) -> FileController:
        return self.file_controller

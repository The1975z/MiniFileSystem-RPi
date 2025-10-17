from typing import List, Optional, Tuple, Callable
from models.file_operations import FileOperations, FileInfo
from models.ssh_connection import SSHConnection
class FileController:
    def __init__(self, ssh_connection: SSHConnection):
        self.ssh_connection = ssh_connection
        self.file_ops = FileOperations()
        self.current_path = "/"
        self.history = ["/"]
        self.history_index = 0
        self.on_directory_change: Optional[Callable[[str], None]] = None
        self.sort_key = "name"
        self.sort_reverse = False
        self.filter_pattern = ""

    def initialize(self):
        if self.ssh_connection.is_connected():
            sftp = self.ssh_connection.get_sftp()
            self.file_ops.set_sftp(sftp)
            self.current_path = self.ssh_connection.get_current_path()
            self.history = [self.current_path]
            self.history_index = 0

    def list_current_directory(self) -> List[FileInfo]:
        files = self.file_ops.list_directory(self.current_path)
        files = self._apply_filter(files)
        files = self._apply_sort(files)
        return files

    def change_directory(self, path: str):
        try:
            self.ssh_connection.change_directory(path)
            self.current_path = self.ssh_connection.get_current_path()

            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]

            self.history.append(self.current_path)
            self.history_index = len(self.history) - 1

            if self.on_directory_change:
                self.on_directory_change(self.current_path)
        except Exception as e:
            print(f"Error changing directory: {e}")

    def go_back(self) -> bool:
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            self.ssh_connection.change_directory(path)
            self.current_path = path

            if self.on_directory_change:
                self.on_directory_change(self.current_path)
            return True
        return False

    def go_forward(self) -> bool:
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            path = self.history[self.history_index]
            self.ssh_connection.change_directory(path)
            self.current_path = path

            if self.on_directory_change:
                self.on_directory_change(self.current_path)
            return True
        return False

    def go_to_parent(self):
        parent = "/".join(self.current_path.rstrip("/").split("/")[:-1]) or "/"
        self.change_directory(parent)

    def create_file(self, filename: str, content: str = "") -> Tuple[bool, str]:
        path = f"{self.current_path}/{filename}"
        return self.file_ops.create_file(path, content)

    def read_file(self, path: str) -> Tuple[bool, str]:
        return self.file_ops.read_file(path)

    def write_file(self, path: str, content: str) -> Tuple[bool, str]:
        return self.file_ops.write_file(path, content)

    def delete_file(self, path: str) -> Tuple[bool, str]:
        return self.file_ops.delete_file(path)

    def create_directory(self, dirname: str) -> Tuple[bool, str]:
        path = f"{self.current_path}/{dirname}"
        return self.file_ops.create_directory(path)

    def delete_directory(self, path: str) -> Tuple[bool, str]:
        return self.file_ops.delete_directory(path)

    def rename(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        old_path = f"{self.current_path}/{old_name}"
        new_path = f"{self.current_path}/{new_name}"
        return self.file_ops.rename(old_path, new_path)

    def move(self, source: str, destination: str) -> Tuple[bool, str]:
        return self.file_ops.move(source, destination)

    def copy(self, source: str, destination: str) -> Tuple[bool, str]:
        return self.file_ops.copy_file(source, destination)

    def change_permissions(self, path: str, mode: int) -> Tuple[bool, str]:
        return self.file_ops.change_permissions(path, mode)

    def get_file_info(self, path: str) -> Optional[FileInfo]:
        return self.file_ops.get_file_stat(path)

    def search_files(self, pattern: str) -> List[FileInfo]:
        return self.file_ops.find_files(self.current_path, pattern)

    def upload_file(self, local_path: str, filename: str) -> Tuple[bool, str]:
        remote_path = f"{self.current_path}/{filename}"
        return self.file_ops.upload_file(local_path, remote_path)

    def download_file(self, remote_path: str, local_path: str) -> Tuple[bool, str]:
        return self.file_ops.download_file(remote_path, local_path)

    def get_disk_usage(self):
        return self.file_ops.get_disk_usage(self.current_path)

    def move_to_recycle(self, path: str) -> Tuple[bool, str]:
        return self.file_ops.move_to_recycle(path)

    def restore_from_recycle(self, filename: str, original_path: str) -> Tuple[bool, str]:
        return self.file_ops.restore_from_recycle(filename, original_path)

    def change_owner(self, path: str, uid: int, gid: int) -> Tuple[bool, str]:
        return self.file_ops.change_owner(path, uid, gid)

    def set_sort(self, sort_key: str, reverse: bool = False):
        self.sort_key = sort_key
        self.sort_reverse = reverse

    def set_filter(self, pattern: str):
        self.filter_pattern = pattern

    def _apply_sort(self, files: List[FileInfo]) -> List[FileInfo]:
        if self.sort_key == "name":
            return sorted(files, key=lambda x: (not x.is_dir, x.name.lower()), reverse=self.sort_reverse)
        elif self.sort_key == "size":
            return sorted(files, key=lambda x: (not x.is_dir, x.size), reverse=self.sort_reverse)
        elif self.sort_key == "modified":
            return sorted(files, key=lambda x: (not x.is_dir, x.modified_time), reverse=self.sort_reverse)
        return files

    def _apply_filter(self, files: List[FileInfo]) -> List[FileInfo]:
        if not self.filter_pattern:
            return files
        pattern = self.filter_pattern.lower()
        return [f for f in files if pattern in f.name.lower()]

import os
import stat
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import paramiko


class FileInfo:
    def __init__(self, name: str, path: str, size: int, is_dir: bool,
                 permissions: str, modified_time: datetime, owner: str = ""):
        self.name = name
        self.path = path
        self.size = size
        self.is_dir = is_dir
        self.permissions = permissions
        self.modified_time = modified_time
        self.owner = owner

    def get_size_str(self) -> str:
        if self.is_dir:
            return "<DIR>"

        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(self.size)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"


class FileOperations:
    def __init__(self, sftp: Optional[paramiko.SFTPClient] = None):
        self.sftp = sftp
        self.recycle_bin_path = ".guios_recycle"

    def set_sftp(self, sftp: Optional[paramiko.SFTPClient]):
        self.sftp = sftp

    def list_directory(self, path: str = ".") -> List[FileInfo]:
        if not self.sftp:
            return []

        try:
            files = []
            for entry in self.sftp.listdir_attr(path):
                is_dir = stat.S_ISDIR(entry.st_mode)
                permissions = self._get_permissions_str(entry.st_mode)
                modified = datetime.fromtimestamp(entry.st_mtime)

                file_info = FileInfo(
                    name=entry.filename,
                    path=os.path.join(path, entry.filename),
                    size=entry.st_size,
                    is_dir=is_dir,
                    permissions=permissions,
                    modified_time=modified,
                    owner=str(entry.st_uid)
                )
                files.append(file_info)

            return sorted(files, key=lambda x: (not x.is_dir, x.name.lower()))
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []

    def create_file(self, path: str, content: str = "") -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            with self.sftp.file(path, 'w') as f:
                f.write(content)
            try:
                self.sftp.chmod(path, 0o644)
            except:
                pass
            return True, "File created successfully"
        except Exception as e:
            return False, str(e)

    def read_file(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            with self.sftp.file(path, 'r') as f:
                content = f.read().decode('utf-8')
            return True, content
        except Exception as e:
            return False, str(e)

    def write_file(self, path: str, content: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            with self.sftp.file(path, 'w') as f:
                f.write(content)
            return True, "File written successfully"
        except Exception as e:
            return False, str(e)

    def delete_file(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            self.sftp.remove(path)
            return True, "File deleted successfully"
        except Exception as e:
            return False, str(e)

    def create_directory(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            self.sftp.mkdir(path)
            try:
                self.sftp.chmod(path, 0o755)
            except:
                pass
            return True, "Directory created successfully"
        except Exception as e:
            return False, str(e)

    def delete_directory(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            self._remove_directory_recursive(path)
            return True, "Directory deleted successfully"
        except Exception as e:
            return False, str(e)

    def rename(self, old_path: str, new_path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            self.sftp.rename(old_path, new_path)
            return True, "Renamed successfully"
        except Exception as e:
            return False, str(e)

    def move(self, source: str, destination: str) -> Tuple[bool, str]:
        return self.rename(source, destination)

    def copy_file(self, source: str, destination: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            success, content = self.read_file(source)
            if not success:
                return False, content

            success, msg = self.write_file(destination, content)
            return success, msg
        except Exception as e:
            return False, str(e)

    def change_permissions(self, path: str, mode: int) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            self.sftp.chmod(path, mode)
            return True, "Permissions changed successfully"
        except Exception as e:
            return False, str(e)

    def get_file_stat(self, path: str) -> Optional[FileInfo]:
        if not self.sftp:
            return None

        try:
            stat_info = self.sftp.stat(path)
            is_dir = stat.S_ISDIR(stat_info.st_mode)
            permissions = self._get_permissions_str(stat_info.st_mode)
            modified = datetime.fromtimestamp(stat_info.st_mtime)

            return FileInfo(
                name=os.path.basename(path),
                path=path,
                size=stat_info.st_size,
                is_dir=is_dir,
                permissions=permissions,
                modified_time=modified,
                owner=str(stat_info.st_uid)
            )
        except Exception as e:
            print(f"Error getting file stat: {e}")
            return None

    def find_files(self, search_path: str, pattern: str) -> List[FileInfo]:
        if not self.sftp:
            return []

        results = []
        try:
            self._search_recursive(search_path, pattern.lower(), results)
        except Exception as e:
            print(f"Error searching files: {e}")

        return results

    def upload_file(self, local_path: str, remote_path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            self.sftp.put(local_path, remote_path)
            try:
                self.sftp.chmod(remote_path, 0o644)
            except:
                pass
            return True, "File uploaded successfully"
        except Exception as e:
            return False, str(e)

    def download_file(self, remote_path: str, local_path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            self.sftp.get(remote_path, local_path)
            return True, "File downloaded successfully"
        except Exception as e:
            return False, str(e)

    def get_disk_usage(self, path: str = "/") -> Dict[str, int]:
        if not self.sftp:
            return {"total": 0, "used": 0, "free": 0}

        try:
            stat_result = self.sftp.statvfs(path)
            total = stat_result.f_blocks * stat_result.f_frsize
            free = stat_result.f_bfree * stat_result.f_frsize
            used = total - free

            return {
                "total": total,
                "used": used,
                "free": free
            }
        except:
            return {"total": 0, "used": 0, "free": 0}

    def move_to_recycle(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            home_dir = self.sftp.normalize(".")
            recycle_path = os.path.join(home_dir, self.recycle_bin_path)

            try:
                self.sftp.stat(recycle_path)
            except FileNotFoundError:
                self.sftp.mkdir(recycle_path)

            filename = os.path.basename(path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{filename}"
            destination = os.path.join(recycle_path, new_filename)

            self.sftp.rename(path, destination)
            return True, "Moved to recycle bin"
        except Exception as e:
            return False, str(e)

    def restore_from_recycle(self, filename: str, original_path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            home_dir = self.sftp.normalize(".")
            recycle_path = os.path.join(home_dir, self.recycle_bin_path)
            source = os.path.join(recycle_path, filename)

            self.sftp.rename(source, original_path)
            return True, "File restored successfully"
        except Exception as e:
            return False, str(e)

    def change_owner(self, path: str, uid: int, gid: int) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"

        try:
            self.sftp.chown(path, uid, gid)
            return True, "Owner changed successfully"
        except Exception as e:
            return False, str(e)

    def _get_permissions_str(self, mode: int) -> str:
        perms = []
        perms.append('d' if stat.S_ISDIR(mode) else '-')
        perms.append('r' if mode & stat.S_IRUSR else '-')
        perms.append('w' if mode & stat.S_IWUSR else '-')
        perms.append('x' if mode & stat.S_IXUSR else '-')
        perms.append('r' if mode & stat.S_IRGRP else '-')
        perms.append('w' if mode & stat.S_IWGRP else '-')
        perms.append('x' if mode & stat.S_IXGRP else '-')
        perms.append('r' if mode & stat.S_IROTH else '-')
        perms.append('w' if mode & stat.S_IWOTH else '-')
        perms.append('x' if mode & stat.S_IXOTH else '-')
        return ''.join(perms)

    def _remove_directory_recursive(self, path: str):
        for item in self.sftp.listdir_attr(path):
            item_path = os.path.join(path, item.filename)
            if stat.S_ISDIR(item.st_mode):
                self._remove_directory_recursive(item_path)
            else:
                self.sftp.remove(item_path)
        self.sftp.rmdir(path)

    def _search_recursive(self, path: str, pattern: str, results: List[FileInfo]):
        try:
            for item in self.sftp.listdir_attr(path):
                item_path = os.path.join(path, item.filename)

                if pattern in item.filename.lower():
                    is_dir = stat.S_ISDIR(item.st_mode)
                    permissions = self._get_permissions_str(item.st_mode)
                    modified = datetime.fromtimestamp(item.st_mtime)

                    results.append(FileInfo(
                        name=item.filename,
                        path=item_path,
                        size=item.st_size,
                        is_dir=is_dir,
                        permissions=permissions,
                        modified_time=modified
                    ))

                if stat.S_ISDIR(item.st_mode):
                    self._search_recursive(item_path, pattern, results)
        except:
            pass

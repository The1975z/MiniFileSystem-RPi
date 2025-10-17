import os
import stat
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import paramiko
import posixpath


# ===== Helper: ใช้กับ "พาธฝั่งรีโมต (Linux/Pi)" เท่านั้น =====
def _posix_abs(p: str) -> str:
    """ทำให้พาธรีโมตเป็น absolute POSIX path เสมอ เช่น '/home/pi'"""
    if not p:
        return "/"
    # ตัดช่องว่าง/quote และแทน backslash -> slash
    p = p.strip().strip('"').strip("'").replace("\\", "/")
    # บีบ // และลบ ./ ../
    p = posixpath.normpath(p)
    # บังคับให้ขึ้นต้นด้วย /
    if not p.startswith("/"):
        p = "/" + p
    return p


def _pjoin(base: str, name: str) -> str:
    """join พาธแบบ POSIX และคืน absolute เสมอ"""
    base = _posix_abs(base)
    name = name or ""
    return _posix_abs(posixpath.join(base, name))


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

    # ---------- List ----------
    def list_directory(self, path: str = ".") -> List[FileInfo]:
        if not self.sftp:
            return []
        try:
            path = _posix_abs(path)
            files = []
            for entry in self.sftp.listdir_attr(path):
                is_dir = stat.S_ISDIR(entry.st_mode)
                permissions = self._get_permissions_str(entry.st_mode)
                modified = datetime.fromtimestamp(entry.st_mtime)
                file_info = FileInfo(
                    name=entry.filename,
                    path=_pjoin(path, entry.filename),   # ✅ POSIX absolute
                    size=getattr(entry, "st_size", 0),
                    is_dir=is_dir,
                    permissions=permissions,
                    modified_time=modified,
                    owner=str(getattr(entry, "st_uid", ""))
                )
                files.append(file_info)
            return sorted(files, key=lambda x: (not x.is_dir, x.name.lower()))
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []

    # ---------- Create / Read / Write ----------
    def create_file(self, path: str, content: str = "") -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            path = _posix_abs(path)
            with self.sftp.file(path, 'w') as f:
                f.write(content)
            try:
                self.sftp.chmod(path, 0o644)
            except Exception:
                pass
            return True, "File created successfully"
        except Exception as e:
            return False, str(e)

    def read_file(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            path = _posix_abs(path)
            with self.sftp.file(path, 'rb') as f:
                data = f.read()
            try:
                content = data.decode('utf-8', errors='replace')
            except Exception:
                content = data.decode('latin-1', errors='replace')
            return True, content
        except Exception as e:
            return False, str(e)

    def write_file(self, path: str, content: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            path = _posix_abs(path)
            with self.sftp.file(path, 'w') as f:
                f.write(content)
            return True, "File written successfully"
        except Exception as e:
            return False, str(e)

    # ---------- Delete / Directory ops ----------
    def delete_file(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            path = _posix_abs(path)
            self.sftp.remove(path)
            return True, "File deleted successfully"
        except Exception as e:
            return False, str(e)

    def create_directory(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            path = _posix_abs(path)
            self.sftp.mkdir(path)
            try:
                self.sftp.chmod(path, 0o755)
            except Exception:
                pass
            return True, "Directory created successfully"
        except Exception as e:
            return False, str(e)

    def delete_directory(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            path = _posix_abs(path)
            self._remove_directory_recursive(path)
            return True, "Directory deleted successfully"
        except Exception as e:
            return False, str(e)

    # ---------- Rename / Move / Copy ----------
    def rename(self, old_path: str, new_path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            old_path = _posix_abs(old_path)
            new_path = _posix_abs(new_path)
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
            source = _posix_abs(source)
            destination = _posix_abs(destination)
            ok, content = self.read_file(source)
            if not ok:
                return False, content
            return self.write_file(destination, content)
        except Exception as e:
            return False, str(e)

    # ---------- Perms / Stat ----------
    def change_permissions(self, path: str, mode: int) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            path = _posix_abs(path)
            self.sftp.chmod(path, mode)
            return True, "Permissions changed successfully"
        except Exception as e:
            return False, str(e)

    def get_file_stat(self, path: str) -> Optional[FileInfo]:
        if not self.sftp:
            return None
        try:
            path = _posix_abs(path)
            stat_info = self.sftp.stat(path)
            is_dir = stat.S_ISDIR(stat_info.st_mode)
            permissions = self._get_permissions_str(stat_info.st_mode)
            modified = datetime.fromtimestamp(stat_info.st_mtime)
            return FileInfo(
                name=posixpath.basename(path),             # ✅ basename แบบ POSIX
                path=path,
                size=getattr(stat_info, "st_size", 0),
                is_dir=is_dir,
                permissions=permissions,
                modified_time=modified,
                owner=str(getattr(stat_info, "st_uid", ""))
            )
        except Exception as e:
            print(f"Error getting file stat: {e}")
            return None

    # ---------- Search ----------
    def find_files(self, search_path: str, pattern: str) -> List[FileInfo]:
        if not self.sftp:
            return []
        results: List[FileInfo] = []
        try:
            search_path = _posix_abs(search_path)
            self._search_recursive(search_path, pattern.lower(), results)
        except Exception as e:
            print(f"Error searching files: {e}")
        return results

    # ---------- Transfer ----------
    def upload_file(self, local_path: str, remote_path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            remote_path = _posix_abs(remote_path)
            self.sftp.put(local_path, remote_path)
            try:
                self.sftp.chmod(remote_path, 0o644)
            except Exception:
                pass
            return True, "File uploaded successfully"
        except Exception as e:
            return False, str(e)

    def download_file(self, remote_path: str, local_path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            remote_path = _posix_abs(remote_path)
            self.sftp.get(remote_path, local_path)
            return True, "File downloaded successfully"
        except Exception as e:
            return False, str(e)

    # ---------- Disk Usage ----------
    def get_disk_usage(self, path: str = "/") -> Dict[str, int]:
        if not self.sftp:
            return {"total": 0, "used": 0, "free": 0}
        try:
            path = _posix_abs(path)
            stat_result = self.sftp.statvfs(path)
            total = stat_result.f_blocks * stat_result.f_frsize
            free = stat_result.f_bfree * stat_result.f_frsize
            used = total - free
            return {"total": total, "used": used, "free": free}
        except Exception:
            return {"total": 0, "used": 0, "free": 0}

    # ---------- Recycle Bin ----------
    def move_to_recycle(self, path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            path = _posix_abs(path)
            home_dir = _posix_abs(self.sftp.normalize("."))  # มักเป็น absolute อยู่แล้ว
            recycle_path = _pjoin(home_dir, self.recycle_bin_path)
            # ensure recycle dir
            try:
                self.sftp.stat(recycle_path)
            except FileNotFoundError:
                self.sftp.mkdir(recycle_path)

            filename = posixpath.basename(path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{filename}"
            destination = _pjoin(recycle_path, new_filename)

            self.sftp.rename(path, destination)
            return True, "Moved to recycle bin"
        except Exception as e:
            return False, str(e)

    def restore_from_recycle(self, filename: str, original_path: str) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            home_dir = _posix_abs(self.sftp.normalize("."))
            recycle_path = _pjoin(home_dir, self.recycle_bin_path)
            source = _pjoin(recycle_path, filename)
            original_path = _posix_abs(original_path)
            self.sftp.rename(source, original_path)
            return True, "File restored successfully"
        except Exception as e:
            return False, str(e)

    def change_owner(self, path: str, uid: int, gid: int) -> Tuple[bool, str]:
        if not self.sftp:
            return False, "Not connected"
        try:
            path = _posix_abs(path)
            self.sftp.chown(path, uid, gid)
            return True, "Owner changed successfully"
        except Exception as e:
            return False, str(e)

    # ---------- Internal helpers ----------
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
        path = _posix_abs(path)
        for item in self.sftp.listdir_attr(path):
            item_path = _pjoin(path, item.filename)  # ✅ POSIX join
            if stat.S_ISDIR(item.st_mode):
                self._remove_directory_recursive(item_path)
            else:
                self.sftp.remove(item_path)
        self.sftp.rmdir(path)

    def _search_recursive(self, path: str, pattern: str, results: List[FileInfo]):
        path = _posix_abs(path)
        try:
            for item in self.sftp.listdir_attr(path):
                item_path = _pjoin(path, item.filename)  # ✅ POSIX join
                if pattern in item.filename.lower():
                    is_dir = stat.S_ISDIR(item.st_mode)
                    permissions = self._get_permissions_str(item.st_mode)
                    modified = datetime.fromtimestamp(item.st_mtime)
                    results.append(FileInfo(
                        name=item.filename,
                        path=item_path,
                        size=getattr(item, "st_size", 0),
                        is_dir=is_dir,
                        permissions=permissions,
                        modified_time=modified
                    ))
                if stat.S_ISDIR(item.st_mode):
                    self._search_recursive(item_path, pattern, results)
        except Exception:
            # ข้ามโฟลเดอร์ที่เข้าไม่ได้/ไม่มีสิทธิ์
            pass

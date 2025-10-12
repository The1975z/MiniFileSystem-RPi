# src/file_manager.py
import os
import shutil 
from src.directory_manager import DirectoryManager

class FileManager:
    """จัดการการเขียน, อ่าน, และจัดการไฟล์/โฟลเดอร์"""
    def __init__(self):
        self.dir_manager = DirectoryManager()

    def write_to_file(self, file_path: str, data: str) -> None:
        
        try:
            directory_path = os.path.dirname(file_path)
            if directory_path:
                self.dir_manager.create_directory(directory_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"Data successfully written to '{file_path}'")
        except IOError as e:
            print(f"Error writing to file {file_path}: {e}")

    def read_from_file(self, file_path: str) -> str | None:

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"--- Content of '{file_path}' ---\n{content}")
                print("------------------------------------")
                return content
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None

    

    def remove_path(self, path: str) -> None:
        """ลบไฟล์หรือโฟลเดอร์"""
        try:
            if os.path.isfile(path):
                os.remove(path)
                print(f"File removed: {path}")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Directory removed: {path}")
            else:
                print(f"Error: Path not found: {path}")
        except OSError as e:
            print(f"Error removing path {path}: {e}")

    def move_path(self, source: str, destination: str) -> None:
        """ย้ายหรือเปลี่ยนชื่อไฟล์/โฟลเดอร์"""
        try:
            shutil.move(source, destination)
            print(f"Moved '{source}' to '{destination}'")
        except (FileNotFoundError, shutil.Error) as e:
            print(f"Error moving path: {e}")

    def copy_path(self, source: str, destination: str) -> None:
        """คัดลอกไฟล์หรือโฟลเดอร์"""
        try:
            if os.path.isfile(source):
                shutil.copy2(source, destination) # ใช้ copy2 เพื่อรักษา metadata
                print(f"Copied file '{source}' to '{destination}'")
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
                print(f"Copied directory '{source}' to '{destination}'")
            else:
                print(f"Error: Source path not found: {source}")
        except (FileNotFoundError, shutil.Error) as e:
            print(f"Error copying path: {e}")
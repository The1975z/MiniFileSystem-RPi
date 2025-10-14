# src/cli_interface.py
import os 
from src.directory_manager import DirectoryManager
from src.file_manager import FileManager
from src.search_engine import SearchEngine
from config import settings

class CLIInterface:
    def __init__(self, root_path=settings.DEFAULT_ROOT_DIR):
        self.root_path = root_path
        self.dir_manager = DirectoryManager()
        self.file_manager = FileManager()
        self.search_engine = SearchEngine()
        self.dir_manager.create_directory(self.root_path)
        print("="*50)
        print(f"Mini File System Initialized. Root is '{self.root_path}'")
        self.show_help()

    def _resolve_path(self, user_path: str) -> str:
        """
        ฟังก์ชันสำคัญ: บังคับให้ path ทั้งหมดอยู่ภายใน root_path ของเรา
        """
        # ป้องกันการใช้ '..' เพื่อทะลุออกจาก root
        if '..' in user_path.split(os.path.sep):
            print("Error: Path traversal ('..') is not allowed.")
            return None

        # ถ้าผู้ใช้พิมพ์ path เต็มมาแล้ว ก็ใช้ได้เลย
        if user_path.startswith(self.root_path):
            return user_path

        # ถ้าพิมพ์มาสั้นๆ ให้เอาไปต่อท้าย root_path
        return os.path.join(self.root_path, user_path)

    def show_help(self):
        
        print("="*50)
        print("Available Commands:")
        print("  mkdir <path>         - Create a directory")
        print("  write <path> \"data\"  - Write data to a file")
        print("  read <path>          - Read data from a file")
        print("  dir [path]           - List contents (like 'ls')")
        print("  tree [path]          - Display directory structure as a tree")
        print("  find <name> [path]   - Find a file")
        print("  rm <path>            - Remove a file or directory")
        print("  mv <src> <dest>      - Move or rename a file or directory")
        print("  cp <src> <dest>      - Copy a file or directory")
        print("  stat <path>          - Show a Detail file or directory")
        print("  help                 - Show this help message")
        print("  exit                 - Exit the program")
        print("="*50)

    def run(self):
        while True:
            try:
                cmd_line = input(f"{settings.CLI_PROMPT}:{self.root_path}> ")
                parts = cmd_line.split(maxsplit=2)
                command = parts[0].lower() if parts else ""

                if command == "exit": break
                elif command == "help": self.show_help()

                
                elif command in ["mkdir", "read", "rm" , "stat"]:
                    if len(parts) > 1:
                        path = self._resolve_path(parts[1])
                        if path:
                            if command == "mkdir": self.dir_manager.create_directory(path)
                            if command == "read": self.file_manager.read_from_file(path)
                            if command == "rm": self.file_manager.remove_path(path)
                            if command == "stat": self.file_manager.stat_file(path)
                    else: print(f"Usage: {command} <path>")

                elif command in ["dir", "tree"]:
                    path_to_show = self._resolve_path(parts[1] if len(parts) > 1 else self.root_path)
                    if path_to_show:
                        if command == "dir": self.dir_manager.list_contents(path_to_show)
                        if command == "tree": self.dir_manager.display_tree(path_to_show)

                elif command == "write":
                    if len(parts) > 2:
                        path = self._resolve_path(parts[1])
                        if path: self.file_manager.write_to_file(path, parts[2].strip('"'))
                    else: print("Usage: write <path> \"data\"")

                elif command in ["mv", "cp"]:
                    if len(parts) > 2:
                        source = self._resolve_path(parts[1])
                        dest = self._resolve_path(parts[2])
                        if source and dest:
                            if command == "mv": self.file_manager.move_path(source, dest)
                            if command == "cp": self.file_manager.copy_path(source, dest)
                    else: print(f"Usage: {command} <source> <destination>")

                elif command == "find":
                    if len(parts) > 1:
                        search_path = self._resolve_path(parts[2] if len(parts) > 2 else self.root_path)
                        if search_path: self.search_engine.find_file(parts[1], search_path)
                    else: print("Usage: find <filename> [path]")

                elif not command: continue
                else: print(f"Unknown command: '{command}'. Type 'help'.")
            except (EOFError, KeyboardInterrupt):
                break
        print("\nExiting Mini File System. Goodbye!")

def main():
    cli = CLIInterface()
    cli.run()
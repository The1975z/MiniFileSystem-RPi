# src/directory_manager.py
import os

class DirectoryManager:
    """จัดการการสร้างและแสดงรายการในไดเรกทอรี"""
    def create_directory(self, path: str) -> None:
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Directory operation successful for: {path}")
        except OSError as e:
            print(f"Error creating directory {path}: {e}")

    def list_contents(self, path: str) -> None:
        print(f"--- Listing contents of '{path}' ---")
        try:
            contents = os.listdir(path)
            if not contents:
                print("(Directory is empty)")
            for item in contents:
                item_type = "d" if os.path.isdir(os.path.join(path, item)) else "f"
                print(f"[{item_type}] {item}")
        except FileNotFoundError:
            print(f"Error: Directory '{path}' not found.")
        print("------------------------------------")

    def display_tree(self, path: str) -> None:
        """แสดงโครงสร้างไฟล์และโฟลเดอร์แบบ tree"""
        print(f"--- Tree view of '{path}' ---")
        if not os.path.isdir(path):
            print(f"Error: Directory '{path}' not found.")
            return

        print(os.path.basename(path))
        self._tree_helper(path, "")
        print("------------------------------------")

    def _tree_helper(self, directory: str, prefix: str):
        """ฟังก์ชันช่วยเหลือสำหรับวนลูปสร้าง tree (Recursive Helper)"""
        try:
            # เรียงลำดับเพื่อให้แสดงผลสวยงาม
            contents = sorted(os.listdir(directory))
            # ตัวชี้สำหรับบอกว่าเป็นรายการสุดท้ายหรือไม่
            pointers = ['├── '] * (len(contents) - 1) + ['└── ']

            for pointer, item in zip(pointers, contents):
                full_path = os.path.join(directory, item)
                print(prefix + pointer + item)

                if os.path.isdir(full_path):
                    
                    extension = '    ' if pointer == '└── ' else '│   '
                    self._tree_helper(full_path, prefix + extension)
        except OSError as e:
            print(f"{prefix}└── [Error reading directory: {e.strerror}]")
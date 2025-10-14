# src/search_engine.py
import os

class SearchEngine:
    """ค้นหาไฟล์ภายในไดเรกทอรีที่กำหนด"""
    def find_file(self, filename: str, search_path: str) -> None:
        print(f"--- Searching for '{filename}' in '{search_path}' ---")
        found_files = []
        for dirpath, _, filenames in os.walk(search_path):
            if filename in filenames:
                found_files.append(os.path.join(dirpath, filename))

        if not found_files:
            print("File not found.")
        else:
            print("Found file(s) at:")
            for path in found_files:
                print(path)
        print("-------------------------------------------------")
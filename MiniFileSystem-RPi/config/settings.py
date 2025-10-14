# config/settings.py
import os

# โฟลเดอร์ root ของ mini FS (สร้างจริงบนดิสก์)
DEFAULT_ROOT_DIR = os.path.join(os.getcwd(), "mini_fs_root")

# prompt ที่แสดงใน CLI
CLI_PROMPT = "mfs"

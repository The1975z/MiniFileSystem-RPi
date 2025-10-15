import customtkinter as ctk
from typing import List, Callable, Optional
from models.file_operations import FileInfo
from views.file_icons import get_file_icon
import tkinter as tk

# --- ค่าคงที่เพื่อให้คอลัมน์ "ตรงกันทุกแถว" ---
NAME_COL_WEIGHT = 3
SIZE_COL_WIDTH  = 120   # px
PERM_COL_WIDTH  = 140   # px
MOD_COL_WIDTH   = 180   # px

ARROW_UP = " ▲"
ARROW_DOWN = " ▼"

class FileBrowser(ctk.CTkFrame):
    def __init__(self, master, title="🌐 เซิร์ฟเวอร์ (Remote)", **kwargs):
        super().__init__(master, **kwargs)

        self.title_text = title
        self.on_file_select: Optional[Callable[[FileInfo], None]] = None
        self.on_file_double_click: Optional[Callable[[FileInfo], None]] = None
        self.on_context_menu: Optional[Callable[[FileInfo, int, int], None]] = None
        self.on_sort: Optional[Callable[[str], None]] = None  # กดหัวคอลัมน์เพื่อ sort

        self._rows_widgets: List[ctk.CTkLabel] = []  # เก็บ widget ทุกชิ้นของทุกแถว เพื่อง่ายต่อการล้าง
        self._header_buttons: Dict[str, ctk.CTkButton] = {}  # เก็บปุ่มหัวคอลัมน์
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Title
        title_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(
            title_frame,
            text=self.title_text,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)

        # Header
        header_frame = ctk.CTkFrame(self, height=30)
        header_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(0, weight=NAME_COL_WEIGHT)
        header_frame.grid_columnconfigure(1, weight=0, minsize=SIZE_COL_WIDTH)
        header_frame.grid_columnconfigure(2, weight=0, minsize=PERM_COL_WIDTH)
        header_frame.grid_columnconfigure(3, weight=0, minsize=MOD_COL_WIDTH)

        self._header_buttons["name"] = ctk.CTkButton(
            header_frame, text="ชื่อไฟล์", fg_color="transparent", hover_color="gray25",
            command=lambda: self.on_sort and self.on_sort("name")
        )
        self._header_buttons["name"].grid(row=0, column=0, padx=10, sticky="w")

        self._header_buttons["size"] = ctk.CTkButton(
            header_frame, text="ขนาด", fg_color="transparent", hover_color="gray25",
            command=lambda: self.on_sort and self.on_sort("size")
        )
        self._header_buttons["size"].grid(row=0, column=1, padx=10, sticky="e")

        ctk.CTkLabel(
            header_frame,
            text="สิทธิ์",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=2, padx=10, sticky="w")

        self._header_buttons["modified"] = ctk.CTkButton(
            header_frame, text="แก้ไขล่าสุด", fg_color="transparent", hover_color="gray25",
            command=lambda: self.on_sort and self.on_sort("modified")
        )
        self._header_buttons["modified"].grid(row=0, column=3, padx=10, sticky="w")

        # Body (Scrollable)
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0, 5))
        # คอนฟิกคอลัมน์ของ “ข้อมูลทุกแถว” ให้เท่ากับ header
        self.scrollable_frame.grid_columnconfigure(0, weight=NAME_COL_WEIGHT)
        self.scrollable_frame.grid_columnconfigure(1, weight=0, minsize=SIZE_COL_WIDTH)
        self.scrollable_frame.grid_columnconfigure(2, weight=0, minsize=PERM_COL_WIDTH)
        self.scrollable_frame.grid_columnconfigure(3, weight=0, minsize=MOD_COL_WIDTH)

    # ---------------- Public API ----------------
    def set_files(self, files: List[FileInfo]):
        # ล้างแถวเก่า
        for w in self._rows_widgets:
            w.destroy()
        self._rows_widgets.clear()

        # วาง “1 แถว = 4 label” ลงใน scrollable_frame โดยตรง
        for r, f in enumerate(files):
            icon = get_file_icon(f.name, f.is_dir)
            name_text = f"{icon} {f.name}"
            size_text = f.get_size_str()
            perm_text = f.permissions
            mod_text  = f.modified_time.strftime("%Y-%m-%d %H:%M") if hasattr(f, "modified_time") else ""

            # ชื่อไฟล์ (col 0)
            name_lbl = ctk.CTkLabel(self.scrollable_frame, text=name_text, anchor="w")
            name_lbl.grid(row=r, column=0, padx=10, pady=5, sticky="w")
            self._bind_row_events(name_lbl, f)

            # ขนาด (col 1, ชิดขวา + width คงที่)
            size_lbl = ctk.CTkLabel(self.scrollable_frame, text=size_text, anchor="e", width=SIZE_COL_WIDTH)
            size_lbl.grid(row=r, column=1, padx=10, pady=5, sticky="e")
            self._bind_row_events(size_lbl, f)

            # สิทธิ์ (col 2)
            perm_lbl = ctk.CTkLabel(self.scrollable_frame, text=perm_text, anchor="w", width=PERM_COL_WIDTH)
            perm_lbl.grid(row=r, column=2, padx=10, pady=5, sticky="w")
            self._bind_row_events(perm_lbl, f)

            # แก้ไขล่าสุด (col 3)
            mod_lbl = ctk.CTkLabel(self.scrollable_frame, text=mod_text, anchor="w", width=MOD_COL_WIDTH)
            mod_lbl.grid(row=r, column=3, padx=10, pady=5, sticky="w")
            self._bind_row_events(mod_lbl, f)

            # เก็บไว้สำหรับลบตอน refresh
            self._rows_widgets.extend([name_lbl, size_lbl, perm_lbl, mod_lbl])

    def clear(self):
        for w in self._rows_widgets:
            w.destroy()
        self._rows_widgets.clear()

        # -------- ลูกศรบอกทิศทางเรียง --------
    def update_sort_indicator(self, key: str, reverse: bool):
        """อัปเดตตัวหนังสือบนหัวคอลัมน์ให้มีลูกศร ▲/▼ ตามคีย์ที่กำลังเรียงอยู่"""
        for k, btn in self._header_buttons.items():
            base = self._base_header_text(k)
            if k == key:
                btn.configure(text=base + (ARROW_DOWN if reverse else ARROW_UP))
            else:
                btn.configure(text=base)

    def _base_header_text(self, key: str) -> str:
        return {
            "name": "ชื่อไฟล์",
            "size": "ขนาด",
            "type": "ประเภท",
            "modified": "แก้ไขล่าสุด",
        }.get(key, key)

    # ---------------- Event helpers ----------------
    def _bind_row_events(self, widget: ctk.CTkLabel, file_info: FileInfo):
        widget.bind("<Button-1>", lambda e: self._emit_select(file_info))
        widget.bind("<Double-Button-1>", lambda e: self._emit_double(file_info))
        widget.bind("<Button-3>", lambda e: self._emit_context(file_info, e))

    def _emit_select(self, f: FileInfo):
        if self.on_file_select:
            self.on_file_select(f)

    def _emit_double(self, f: FileInfo):
        if self.on_file_double_click:
            self.on_file_double_click(f)

    def _emit_context(self, f: FileInfo, event: tk.Event):
        if self.on_context_menu:
            self.on_context_menu(f, event.x_root, event.y_root)

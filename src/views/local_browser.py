import customtkinter as ctk
import os
from typing import Callable, Optional, List
from datetime import datetime
from pathlib import Path
import tkinter as tk
from views.file_icons import get_file_icon
class LocalFileInfo:
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.is_dir = os.path.isdir(path)

        try:
            stat = os.stat(path)
            self.size = stat.st_size if not self.is_dir else 0
            self.modified_time = datetime.fromtimestamp(stat.st_mtime)
        except:
            self.size = 0
            self.modified_time = datetime.now()

    def get_size_str(self) -> str:
        if self.is_dir:
            return "<โฟลเดอร์>"

        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(self.size)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"


class LocalBrowser(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.current_path = str(Path.home())
        self.on_file_select: Optional[Callable] = None
        self.on_file_double_click: Optional[Callable] = None
        self.on_drop: Optional[Callable] = None

        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            title_frame,
            text="💻 เครื่องของฉัน (Local)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)

        toolbar_frame = ctk.CTkFrame(self, height=40)
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        toolbar_frame.grid_columnconfigure(1, weight=1)

        self.up_btn = ctk.CTkButton(
            toolbar_frame,
            text="↑",
            width=40,
            command=self._go_up
        )
        self.up_btn.grid(row=0, column=0, padx=5)

        self.path_entry = ctk.CTkEntry(toolbar_frame)
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.path_entry.bind("<Return>", self._on_path_enter)

        refresh_btn = ctk.CTkButton(
            toolbar_frame,
            text="🔄",
            width=40,
            command=self.refresh
        )
        refresh_btn.grid(row=0, column=2, padx=5)

        header_frame = ctk.CTkFrame(self, height=30)
        header_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))
        header_frame.grid_columnconfigure(0, weight=3)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=2)

        ctk.CTkLabel(
            header_frame,
            text="ชื่อไฟล์",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, padx=10, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="ขนาด",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, padx=10, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="แก้ไขล่าสุด",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=2, padx=10, sticky="w")

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.file_items = []

    def _go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.refresh()

    def _on_path_enter(self, event):
        path = self.path_entry.get()
        if os.path.exists(path):
            self.current_path = path
            self.refresh()

    def refresh(self):
        for item in self.file_items:
            item.destroy()
        self.file_items.clear()

        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, self.current_path)

        try:
            entries = os.listdir(self.current_path)
            files = []

            for entry in entries:
                try:
                    full_path = os.path.join(self.current_path, entry)
                    file_info = LocalFileInfo(full_path)
                    files.append(file_info)
                except:
                    continue

            files.sort(key=lambda x: (not x.is_dir, x.name.lower()))

            for file_info in files:
                item = LocalFileItem(
                    self.scrollable_frame,
                    file_info,
                    on_click=lambda f=file_info: self._on_item_click(f),
                    on_double_click=lambda f=file_info: self._on_item_double_click(f)
                )
                item.pack(fill="x", pady=2)
                self.file_items.append(item)
        except Exception as e:
            print(f"Error listing directory: {e}")

    def _on_item_click(self, file_info):
        if self.on_file_select:
            self.on_file_select(file_info)

    def _on_item_double_click(self, file_info):
        if file_info.is_dir:
            self.current_path = file_info.path
            self.refresh()
        elif self.on_file_double_click:
            self.on_file_double_click(file_info)

    def get_selected_files(self) -> List[str]:
        return []


class LocalFileItem(ctk.CTkFrame):
    def __init__(self, master, file_info: LocalFileInfo, on_click=None, on_double_click=None, **kwargs):
        super().__init__(master, **kwargs)

        self.file_info = file_info
        self.on_click = on_click
        self.on_double_click = on_double_click

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)

        icon = get_file_icon(file_info.name, file_info.is_dir)
        name_text = f"{icon} {file_info.name}"

        self.name_label = ctk.CTkLabel(self, text=name_text, anchor="w")
        self.name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.size_label = ctk.CTkLabel(self, text=file_info.get_size_str(), anchor="w")
        self.size_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.modified_label = ctk.CTkLabel(
            self,
            text=file_info.modified_time.strftime("%Y-%m-%d %H:%M"),
            anchor="w"
        )
        self.modified_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.bind("<Button-1>", self._handle_click)
        self.bind("<Double-Button-1>", self._handle_double_click)

        for child in self.winfo_children():
            child.bind("<Button-1>", self._handle_click)
            child.bind("<Double-Button-1>", self._handle_double_click)

    def _handle_click(self, event):
        if self.on_click:
            self.on_click()

    def _handle_double_click(self, event):
        if self.on_double_click:
            self.on_double_click()

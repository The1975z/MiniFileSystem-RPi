import customtkinter as ctk
from typing import List, Callable, Optional
from models.file_operations import FileInfo
from views.file_icons import get_file_icon
import tkinter as tk
class FileBrowser(ctk.CTkFrame):
    def __init__(self, master, title="🌐 เซิร์ฟเวอร์ (Remote)", **kwargs):
        super().__init__(master, **kwargs)

        self.title_text = title
        self.on_file_select: Optional[Callable[[FileInfo], None]] = None
        self.on_file_double_click: Optional[Callable[[FileInfo], None]] = None
        self.on_context_menu: Optional[Callable[[FileInfo, int, int], None]] = None

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            title_frame,
            text=self.title_text,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)

        header_frame = ctk.CTkFrame(self, height=30)
        header_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(0, weight=3)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=2)

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
            text="สิทธิ์",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=2, padx=10, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="แก้ไขล่าสุด",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=3, padx=10, sticky="w")

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.file_items = []

    def set_files(self, files: List[FileInfo]):
        for item in self.file_items:
            item.destroy()
        self.file_items.clear()

        for file_info in files:
            item = FileItem(
                self.scrollable_frame,
                file_info,
                on_click=lambda f=file_info: self._on_item_click(f),
                on_double_click=lambda f=file_info: self._on_item_double_click(f),
                on_right_click=lambda e, f=file_info: self._on_item_right_click(f, e)
            )
            item.pack(fill="x", pady=2)
            self.file_items.append(item)

    def _on_item_click(self, file_info: FileInfo):
        if self.on_file_select:
            self.on_file_select(file_info)

    def _on_item_double_click(self, file_info: FileInfo):
        if self.on_file_double_click:
            self.on_file_double_click(file_info)

    def _on_item_right_click(self, file_info: FileInfo, event):
        if self.on_context_menu and event:
            self.on_context_menu(file_info, event.x_root, event.y_root)

    def clear(self):
        for item in self.file_items:
            item.destroy()
        self.file_items.clear()


class FileItem(ctk.CTkFrame):
    def __init__(self, master, file_info: FileInfo, on_click=None,
                 on_double_click=None, on_right_click=None, **kwargs):
        super().__init__(master, **kwargs)

        self.file_info = file_info
        self.on_click = on_click
        self.on_double_click = on_double_click
        self.on_right_click = on_right_click

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=2)

        icon = get_file_icon(file_info.name, file_info.is_dir)
        name_text = f"{icon} {file_info.name}"

        self.name_label = ctk.CTkLabel(
            self,
            text=name_text,
            anchor="w"
        )
        self.name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.size_label = ctk.CTkLabel(
            self,
            text=file_info.get_size_str(),
            anchor="w"
        )
        self.size_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.perm_label = ctk.CTkLabel(
            self,
            text=file_info.permissions,
            anchor="w"
        )
        self.perm_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.modified_label = ctk.CTkLabel(
            self,
            text=file_info.modified_time.strftime("%Y-%m-%d %H:%M"),
            anchor="w"
        )
        self.modified_label.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        self.bind("<Button-1>", self._handle_click)
        self.bind("<Double-Button-1>", self._handle_double_click)
        self.bind("<Button-3>", self._handle_right_click)

        for child in self.winfo_children():
            child.bind("<Button-1>", self._handle_click)
            child.bind("<Double-Button-1>", self._handle_double_click)
            child.bind("<Button-3>", self._handle_right_click)

    def _handle_click(self, event):
        if self.on_click:
            self.on_click()

    def _handle_double_click(self, event):
        if self.on_double_click:
            self.on_double_click()

    def _handle_right_click(self, event):
        if self.on_right_click:
            self.on_right_click(event)

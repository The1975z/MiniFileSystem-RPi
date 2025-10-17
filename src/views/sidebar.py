import customtkinter as ctk
from typing import Callable, Optional
class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=200, corner_radius=0, **kwargs)

        self.on_connect: Optional[Callable] = None
        self.on_load_config: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
        self.on_refresh: Optional[Callable] = None
        self.on_upload: Optional[Callable] = None
        self.on_download: Optional[Callable] = None
        self.on_new_file: Optional[Callable] = None
        self.on_new_folder: Optional[Callable] = None
        self.on_delete: Optional[Callable] = None
        self.on_appearance_change: Optional[Callable] = None
        self.on_language_change: Optional[Callable] = None

        self._setup_ui()

    def _setup_ui(self):
        self.grid_rowconfigure(9, weight=1)

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=10, pady=(20, 10))

        ctk.CTkLabel(
            title_frame,
            text="FILE-MANAGEMENT",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack()

        ctk.CTkLabel(
            title_frame,
            text="SYSTEM-OS",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack()

        self.connect_btn = ctk.CTkButton(
            self,
            text="🔌 เชื่อมต่อ",
            command=self._handle_connect
        )
        self.connect_btn.grid(row=1, column=0, padx=20, pady=10)

        self.load_config_btn = ctk.CTkButton(
            self,
            text="📋 โหลดการเชื่อมต่อ",
            command=self._handle_load_config,
            fg_color="gray40",
            hover_color="gray30"
        )
        self.load_config_btn.grid(row=2, column=0, padx=20, pady=5)

        self.disconnect_btn = ctk.CTkButton(
            self,
            text="🔌 ตัดการเชื่อมต่อ",
            command=self._handle_disconnect,
            state="disabled"
        )
        self.disconnect_btn.grid(row=3, column=0, padx=20, pady=10)

        separator = ctk.CTkFrame(self, height=2, fg_color="gray")
        separator.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.refresh_btn = ctk.CTkButton(
            self,
            text="🔄 รีเฟรช",
            command=self._handle_refresh,
            state="disabled"
        )
        self.refresh_btn.grid(row=5, column=0, padx=20, pady=10)

        self.new_file_btn = ctk.CTkButton(
            self,
            text="📄 ไฟล์ใหม่",
            command=self._handle_new_file,
            state="disabled"
        )
        self.new_file_btn.grid(row=6, column=0, padx=20, pady=10)

        self.new_folder_btn = ctk.CTkButton(
            self,
            text="📁 โฟลเดอร์ใหม่",
            command=self._handle_new_folder,
            state="disabled"
        )
        self.new_folder_btn.grid(row=7, column=0, padx=20, pady=10)

        self.delete_btn = ctk.CTkButton(
            self,
            text="🗑️ ลบไฟล์/โฟลเดอร์",
            command=self._handle_delete,
            state="disabled"
        )
        self.delete_btn.grid(row=8, column=0, padx=20, pady=10)

        self.upload_btn = ctk.CTkButton(
            self,
            text="📤 อัปโหลด",
            command=self._handle_upload,
            state="disabled"
        )
        self.upload_btn.grid(row=9, column=0, padx=20, pady=10)

        self.language_label = ctk.CTkLabel(
            self,
            text="ภาษา:",
            anchor="w"
        )
        self.language_label.grid(row=10, column=0, padx=20, pady=(10, 0))

        self.language_menu = ctk.CTkOptionMenu(
            self,
            values=["ไทย 🇹🇭", "English 🇬🇧"],
            command=self._handle_language_change
        )
        self.language_menu.set("ไทย 🇹🇭")
        self.language_menu.grid(row=11, column=0, padx=20, pady=(10, 10))

        self.appearance_label = ctk.CTkLabel(
            self,
            text="รูปแบบ:",
            anchor="w"
        )
        self.appearance_label.grid(row=12, column=0, padx=20, pady=(10, 0))

        self.appearance_menu = ctk.CTkOptionMenu(
            self,
            values=["สว่าง", "มืด", "ระบบ"],
            command=self._handle_appearance_change
        )
        self.appearance_menu.set("มืด")
        self.appearance_menu.grid(row=13, column=0, padx=20, pady=(10, 20))

    def set_connected(self, connected: bool):
        if connected:
            self.connect_btn.configure(state="disabled")
            self.disconnect_btn.configure(state="normal")
            self.refresh_btn.configure(state="normal")
            self.new_file_btn.configure(state="normal")
            self.new_folder_btn.configure(state="normal")
            self.upload_btn.configure(state="normal")
        else:
            self.connect_btn.configure(state="normal")
            self.disconnect_btn.configure(state="disabled")
            self.refresh_btn.configure(state="disabled")
            self.new_file_btn.configure(state="disabled")
            self.new_folder_btn.configure(state="disabled")
            self.upload_btn.configure(state="disabled")

    def _handle_connect(self):
        if self.on_connect:
            self.on_connect()

    def _handle_load_config(self):
        if self.on_load_config:
            self.on_load_config()

    def _handle_disconnect(self):
        if self.on_disconnect:
            self.on_disconnect()

    def _handle_refresh(self):
        if self.on_refresh:
            self.on_refresh()

    def _handle_upload(self):
        if self.on_upload:
            self.on_upload()

    def _handle_download(self):
        if self.on_download:
            self.on_download()

    def _handle_new_file(self):
        if self.on_new_file:
            self.on_new_file()

    def _handle_new_folder(self):
        if self.on_new_folder:
            self.on_new_folder()

    def _handle_delete(self):
        if self.on_delete:
            self.on_delete()

    def _handle_language_change(self, lang: str):
        if self.on_language_change:
            self.on_language_change(lang)

    def _handle_appearance_change(self, mode: str):
        mode_map = {
            "สว่าง": "Light",
            "มืด": "Dark",
            "ระบบ": "System",
            "Light": "Light",
            "Dark": "Dark",
            "System": "System"
        }
        actual_mode = mode_map.get(mode, mode)
        if self.on_appearance_change:
            self.on_appearance_change(actual_mode)

    def update_language(self, texts: dict):
        self.connect_btn.configure(text=texts.get("connect", "🔌 เชื่อมต่อ"))
        self.disconnect_btn.configure(text=texts.get("disconnect", "🔌 ตัดการเชื่อมต่อ"))
        self.refresh_btn.configure(text=texts.get("refresh", "🔄 รีเฟรช"))
        self.new_file_btn.configure(text=texts.get("new_file", "📄 ไฟล์ใหม่"))
        self.new_folder_btn.configure(text=texts.get("new_folder", "📁 โฟลเดอร์ใหม่"))
        self.upload_btn.configure(text=texts.get("upload", "📤 อัปโหลด"))
        self.language_label.configure(text=texts.get("language", "ภาษา:"))
        self.appearance_label.configure(text=texts.get("appearance", "รูปแบบ:"))

        current_appearance = self.appearance_menu.get()
        if current_appearance in ["สว่าง", "Light"]:
            self.appearance_menu.configure(values=[texts.get("light"), texts.get("dark"), texts.get("system")])
            self.appearance_menu.set(texts.get("light"))
        elif current_appearance in ["มืด", "Dark"]:
            self.appearance_menu.configure(values=[texts.get("light"), texts.get("dark"), texts.get("system")])
            self.appearance_menu.set(texts.get("dark"))
        else:
            self.appearance_menu.configure(values=[texts.get("light"), texts.get("dark"), texts.get("system")])
            self.appearance_menu.set(texts.get("system"))

    def _handle_delete(self):
        if self.on_delete:
            self.on_delete()
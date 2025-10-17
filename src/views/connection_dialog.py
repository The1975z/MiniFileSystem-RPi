import customtkinter as ctk
from typing import Optional, Callable
from tkinter import filedialog
class ConnectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, saved_connections=None):
        super().__init__(parent)

        self.title("เชื่อมต่อเซิร์ฟเวอร์")
        self.geometry("520x700")
        self.resizable(False, False)

        self.result = None
        self.saved_connections = saved_connections or []
        self.on_connect: Optional[Callable] = None
        self.on_save: Optional[Callable] = None
        self.password_visible = False

        self._setup_ui()
        self.grab_set()

    def _setup_ui(self):
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        title_label = ctk.CTkLabel(
            main_container,
            text="เชื่อมต่อเซิร์ฟเวอร์",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(0, 15))

        scrollable_frame = ctk.CTkScrollableFrame(main_container, height=500)
        scrollable_frame.pack(fill="both", expand=True, pady=(0, 15))

        if self.saved_connections:
            saved_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            saved_frame.pack(fill="x", pady=(0, 15))

            ctk.CTkLabel(
                saved_frame,
                text="การเชื่อมต่อที่บันทึกไว้:",
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(anchor="w", pady=(0, 5))

            self.saved_combo = ctk.CTkComboBox(
                saved_frame,
                values=self.saved_connections,
                command=self._on_saved_selected,
                height=35
            )
            self.saved_combo.pack(fill="x", pady=(0, 5))

        form_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)

        fields = [
            ("ชื่อการเชื่อมต่อ:", "name_entry", "เซิร์ฟเวอร์ของฉัน", None),
            ("โปรโตคอล:", "protocol_combo", None, ["SFTP", "SCP", "FTP", "FTPS", "HTTP"]),
            ("ชื่อโฮสต์:", "host_entry", "100.100.144.94", None),
            ("พอร์ต:", "port_entry", "2222", None),
            ("ชื่อผู้ใช้:", "username_entry", "username", None),
        ]

        for label_text, attr_name, placeholder, values in fields:
            ctk.CTkLabel(
                form_frame,
                text=label_text,
                font=ctk.CTkFont(size=12)
            ).pack(anchor="w", pady=(10, 3))

            if values:
                widget = ctk.CTkComboBox(form_frame, values=values, height=35)
                widget.set("SFTP")
                setattr(self, attr_name, widget)
                widget.pack(fill="x", pady=(0, 5))
            else:
                widget = ctk.CTkEntry(form_frame, placeholder_text=placeholder, height=35)
                if attr_name == "port_entry":
                    widget.insert(0, "22")
                setattr(self, attr_name, widget)
                widget.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            form_frame,
            text="รหัสผ่าน:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(10, 3))
        
        password_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_container.pack(fill="x", pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            password_container,
            placeholder_text="รหัสผ่าน",
            show="*",
            height=35
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.toggle_password_btn = ctk.CTkButton(
            password_container,
            text="👁",
            width=45,
            height=35,
            command=self._toggle_password,
            font=ctk.CTkFont(size=16)
        )
        self.toggle_password_btn.pack(side="right")

        ctk.CTkLabel(
            form_frame,
            text="ไฟล์คีย์ (SSH Key):",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(10, 3))
        
        key_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        key_container.pack(fill="x", pady=(0, 5))

        self.key_entry = ctk.CTkEntry(
            key_container,
            placeholder_text="เส้นทางไปยังไฟล์คีย์",
            height=35
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            key_container,
            text="เลือกไฟล์",
            width=100,
            height=35,
            command=self._browse_key
        )
        browse_btn.pack(side="right")

        button_container = ctk.CTkFrame(main_container, fg_color="transparent")
        button_container.pack(fill="x", pady=(5, 0))

        self.save_check = ctk.CTkCheckBox(
            button_container,
            text="บันทึกการเชื่อมต่อ",
            font=ctk.CTkFont(size=12)
        )
        self.save_check.pack(side="left", padx=5)

        button_right_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        button_right_frame.pack(side="right", padx=5)

        connect_btn = ctk.CTkButton(
            button_right_frame,
            text="เชื่อมต่อ",
            command=self._on_connect_click,
            width=100,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        connect_btn.pack(side="right", padx=(8, 0))

        cancel_btn = ctk.CTkButton(
            button_right_frame,
            text="ยกเลิก",
            command=self._on_cancel,
            fg_color="gray40",
            hover_color="gray30",
            width=100,
            height=38,
            font=ctk.CTkFont(size=13)
        )
        cancel_btn.pack(side="right")

    def _toggle_password(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_entry.configure(show="")
            self.toggle_password_btn.configure(text="🙈")
        else:
            self.password_entry.configure(show="*")
            self.toggle_password_btn.configure(text="👁")

    def _browse_key(self):
        filename = filedialog.askopenfilename(
            title="เลือกไฟล์ SSH Key",
            filetypes=[("All Files", "*.*"), ("PEM Files", "*.pem"), ("Key Files", "*.key")]
        )
        if filename:
            self.key_entry.delete(0, "end")
            self.key_entry.insert(0, filename)

    def _on_saved_selected(self, choice):
        if self.on_save:
            config = self.on_save(choice)
            if config:
                self.name_entry.delete(0, "end")
                self.name_entry.insert(0, config.name)
                self.host_entry.delete(0, "end")
                self.host_entry.insert(0, config.host)
                self.port_entry.delete(0, "end")
                self.port_entry.insert(0, str(config.port))
                self.username_entry.delete(0, "end")
                self.username_entry.insert(0, config.username)
                if config.password:
                    self.password_entry.delete(0, "end")
                    self.password_entry.insert(0, config.password)
                if config.identity_file:
                    self.key_entry.delete(0, "end")
                    self.key_entry.insert(0, config.identity_file)
                self.protocol_combo.set(config.protocol)

    def _on_connect_click(self):
        try:
            port = int(self.port_entry.get())
        except ValueError:
            port = 22

        self.result = {
            "name": self.name_entry.get(),
            "host": self.host_entry.get(),
            "port": port,
            "username": self.username_entry.get(),
            "password": self.password_entry.get() or None,
            "identity_file": self.key_entry.get() or None,
            "protocol": self.protocol_combo.get(),
            "save": self.save_check.get()
        }

        if self.on_connect:
            self.on_connect(self.result)

        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def get_result(self):
        return self.result
import customtkinter as ctk
from typing import Optional


class PassphraseDialog(ctk.CTkToplevel):
    def __init__(self, parent, lang_texts: dict, key_path: str = ""):
        super().__init__(parent)

        self.title(lang_texts.get("title", "Passphrase Required"))
        self.geometry("500x380")
        self.resizable(False, False)

        self.lang_texts = lang_texts
        self.key_path = key_path
        self.passphrase = None
        self.password_visible = False

        self._setup_ui()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.after(50, lambda: self.lift())
        self.after(50, lambda: self.focus_force())
        self.after(100, lambda: self.passphrase_entry.focus())

    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        title_label = ctk.CTkLabel(
            main_frame,
            text=self.lang_texts.get("title", "Passphrase Required"),
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        icon_label = ctk.CTkLabel(
            main_frame,
            text="🔐",
            font=ctk.CTkFont(size=64)
        )
        icon_label.pack(pady=(5, 20))

        message_label = ctk.CTkLabel(
            main_frame,
            text=self.lang_texts.get("message", "Enter passphrase"),
            font=ctk.CTkFont(size=13),
            wraplength=420,
            justify="center"
        )
        message_label.pack(pady=(0, 15))

        if self.key_path:
            key_frame = ctk.CTkFrame(main_frame, fg_color="gray25", corner_radius=8)
            key_frame.pack(fill="x", pady=(0, 20), padx=10)
            
            key_label = ctk.CTkLabel(
                key_frame,
                text=f"Key: {self.key_path}",
                font=ctk.CTkFont(size=11),
                text_color="gray70"
            )
            key_label.pack(pady=10, padx=15)

        passphrase_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        passphrase_container.pack(fill="x", pady=(0, 25), padx=10)

        self.passphrase_entry = ctk.CTkEntry(
            passphrase_container,
            placeholder_text=self.lang_texts.get("placeholder", "Enter passphrase"),
            show="*",
            height=45,
            font=ctk.CTkFont(size=14),
            border_width=2,
            corner_radius=8
        )
        self.passphrase_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.passphrase_entry.bind("<Return>", lambda e: self._on_ok())
        self.passphrase_entry.bind("<Escape>", lambda e: self._on_cancel())

        self.toggle_btn = ctk.CTkButton(
            passphrase_container,
            text="👁",
            width=50,
            height=45,
            command=self._toggle_visibility,
            font=ctk.CTkFont(size=18),
            corner_radius=8
        )
        self.toggle_btn.pack(side="right")

        button_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_container.pack(fill="x", padx=10)

        button_right_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        button_right_frame.pack(side="right")

        ok_btn = ctk.CTkButton(
            button_right_frame,
            text=self.lang_texts.get("ok", "OK"),
            command=self._on_ok,
            width=120,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10
        )
        ok_btn.pack(side="right", padx=(10, 0))

        cancel_btn = ctk.CTkButton(
            button_right_frame,
            text=self.lang_texts.get("cancel", "Cancel"),
            command=self._on_cancel,
            fg_color="gray40",
            hover_color="gray30",
            width=120,
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10
        )
        cancel_btn.pack(side="right")

    def _toggle_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.passphrase_entry.configure(show="")
            self.toggle_btn.configure(text="🙈")
        else:
            self.passphrase_entry.configure(show="*")
            self.toggle_btn.configure(text="👁")

    def _on_ok(self):
        self.passphrase = self.passphrase_entry.get()
        self.grab_release()
        self.destroy()

    def _on_cancel(self):
        self.passphrase = None
        self.grab_release()
        self.destroy()

    def get_passphrase(self) -> Optional[str]:
        return self.passphrase
import customtkinter as ctk
from typing import Optional
import threading
import time
class ConnectionProgressDialog(ctk.CTkToplevel):
    def __init__(self, parent, lang_texts: dict):
        super().__init__(parent)

        self.title(lang_texts.get("title", "Connecting..."))
        self.geometry("600x400")
        self.resizable(False, False)

        self.lang_texts = lang_texts
        self.is_cancelled = False

        self._setup_ui()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            main_frame,
            text=self.lang_texts.get("title", "Connecting..."),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        self.progress = ctk.CTkProgressBar(main_frame, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0, 20))
        self.progress.start()

        self.status_text = ctk.CTkTextbox(
            main_frame,
            height=250,
            font=ctk.CTkFont(family="Courier New", size=11),
            wrap="word"
        )
        self.status_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.status_text.configure(state="disabled")

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel / ยกเลิก",
            command=self._on_cancel,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.cancel_btn.pack(side="right")

    def add_status(self, message: str):
        self.status_text.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert("end", f"[{timestamp}] {message}\n\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")
        self.update()

    def set_progress_mode(self, mode: str):
        if mode == "determinate":
            self.progress.stop()
            self.progress.configure(mode="determinate")
        else:
            self.progress.configure(mode="indeterminate")
            self.progress.start()

    def set_progress_value(self, value: float):
        self.progress.set(value)

    def set_success(self):
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self.progress.set(1.0)
        self.cancel_btn.configure(text="Close / ปิด", command=self._on_close)

    def set_failed(self):
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self.progress.set(0)
        self.cancel_btn.configure(text="Close / ปิด", command=self._on_close, fg_color="red")

    def _on_cancel(self):
        self.is_cancelled = True
        self._on_close()

    def _on_close(self):
        self.grab_release()
        self.destroy()

    def simulate_connection(self, host: str, username: str, key_comment: str = ""):
        steps = [
            ("searching_host", 1.0),
            ("connecting", 1.5),
            ("authenticating", 1.0),
            ("using_username", 0.5),
            ("auth_public_key", 1.5),
            ("loading_keys", 1.0),
            ("success", 0.5)
        ]

        for step_key, delay in steps:
            if self.is_cancelled:
                return

            message = self.lang_texts.get(step_key, step_key)
            message = message.format(username=username, key=key_comment or "default")
            self.add_status(message)
            time.sleep(delay)

        self.set_success()

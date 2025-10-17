import customtkinter as ctk
from typing import Optional, Callable
import threading


class TerminalView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.on_command: Optional[Callable[[str], None]] = None
        self.username = ""
        self.hostname = ""
        self.current_directory = "~"
        self.command_history = []
        self.history_index = -1
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            title_frame,
            text="💻 Terminal (SSH)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)

        self.output_text = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=("#0c0c0c", "#0c0c0c"),
            text_color=("#00ff00", "#00ff00"),
            wrap="none"
        )
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        input_frame = ctk.CTkFrame(self, fg_color=("#1a1a1a", "#0c0c0c"))
        input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)

        self.prompt_label = ctk.CTkLabel(
            input_frame,
            text="$",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color=("#00ff00", "#00ff00")
        )
        self.prompt_label.grid(row=0, column=0, padx=(15, 5), pady=10)

        self.command_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="พิมพ์คำสั่ง...",
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=("#1a1a1a", "#0c0c0c"),
            text_color=("#00ff00", "#00ff00"),
            border_width=0
        )
        self.command_entry.grid(row=0, column=1, sticky="ew", pady=10)
        self.command_entry.bind("<Return>", self._on_command_enter)
        self.command_entry.bind("<Up>", self._history_up)
        self.command_entry.bind("<Down>", self._history_down)

    def _on_command_enter(self, event):
        self._send_command()

    def _history_up(self, event):
        if not self.command_history:
            return
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, self.command_history[-(self.history_index + 1)])

    def _history_down(self, event):
        if self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, self.command_history[-(self.history_index + 1)])
        elif self.history_index == 0:
            self.history_index = -1
            self.command_entry.delete(0, "end")

    def _send_command(self):
        command = self.command_entry.get().strip()
        if not command:
            return

        self.command_history.append(command)
        self.history_index = -1

        prompt = self._get_prompt()
        self.append_output(f"{prompt}{command}\n", "command")
        self.command_entry.delete(0, "end")

        if self.on_command:
            threading.Thread(target=self._execute_command, args=(command,), daemon=True).start()

    def _execute_command(self, command):
        if self.on_command:
            self.on_command(command)

    def _get_prompt(self):
        if self.username and self.hostname:
            return f"{self.username}@{self.hostname}:{self.current_directory}$ "
        return "$ "

    def _update_prompt(self):
        prompt = self._get_prompt()
        self.prompt_label.configure(text=prompt)

    def append_output(self, text: str, tag: str = "output"):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", text)
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def clear_output(self):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        self.command_history = []
        self.history_index = -1

    def write_welcome(self, hostname: str, username: str):
        self.username = username
        self.hostname = hostname
        self.current_directory = "~"
        self._update_prompt()

        welcome_text = f"""╔═══════════════════════════════════════════╗
║   FILE MANAGEMENT SYSTEM - OS             ║
║   SSH Terminal Connected                  ║
╚═══════════════════════════════════════════╝

Connected to: {username}@{hostname}
Type your Linux commands below. Use Up/Down arrows for command history.

"""
        self.append_output(welcome_text, "welcome")

    def update_current_directory(self, directory: str):
        self.current_directory = directory
        self._update_prompt()

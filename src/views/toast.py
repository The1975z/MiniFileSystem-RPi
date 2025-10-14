import customtkinter as ctk
import threading


class Toast:
    @staticmethod
    def show(parent, message: str, duration: int = 3000, toast_type: str = "info"):
        toast = ctk.CTkToplevel(parent)
        toast.withdraw()
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)

        colors = {
            "success": ("#2ecc71", "#27ae60"),
            "error": ("#e74c3c", "#c0392b"),
            "warning": ("#f39c12", "#e67e22"),
            "info": ("#3498db", "#2980b9")
        }

        icons = {
            "success": "✓",
            "error": "✗",
            "warning": "⚠",
            "info": "ℹ"
        }

        bg_color, border_color = colors.get(toast_type, colors["info"])
        icon = icons.get(toast_type, icons["info"])

        frame = ctk.CTkFrame(
            toast,
            fg_color=bg_color,
            corner_radius=10,
            border_width=2,
            border_color=border_color
        )
        frame.pack(padx=2, pady=2)

        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(padx=15, pady=10)

        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        icon_label.pack(side="left", padx=(0, 10))

        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color="white",
            wraplength=350
        )
        message_label.pack(side="left")

        parent.update_idletasks()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()

        toast.update_idletasks()
        toast_width = toast.winfo_reqwidth()
        toast_height = toast.winfo_reqheight()

        x = parent_x + (parent_width - toast_width) // 2
        y = parent_y + parent_height - toast_height - 50

        toast.geometry(f"+{x}+{y}")
        toast.deiconify()

        def fade_out():
            try:
                for i in range(10, -1, -1):
                    alpha = i / 10
                    toast.attributes('-alpha', alpha)
                    toast.update()
                    threading.Event().wait(0.03)
                toast.destroy()
            except:
                pass

        def auto_close():
            threading.Event().wait(duration / 1000)
            if toast.winfo_exists():
                fade_out()

        threading.Thread(target=auto_close, daemon=True).start()

        return toast

    @staticmethod
    def success(parent, message: str, duration: int = 3000):
        return Toast.show(parent, message, duration, "success")

    @staticmethod
    def error(parent, message: str, duration: int = 4000):
        return Toast.show(parent, message, duration, "error")

    @staticmethod
    def warning(parent, message: str, duration: int = 3500):
        return Toast.show(parent, message, duration, "warning")

    @staticmethod
    def info(parent, message: str, duration: int = 3000):
        return Toast.show(parent, message, duration, "info")

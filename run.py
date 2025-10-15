import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
from views.main_view import MainView


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = MainView()
    app.mainloop()


if __name__ == "__main__":
    main()

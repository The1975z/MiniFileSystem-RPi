import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from utils.logger import logger
from views.main_view import MainView


def main():
    try:
        logger.info("Starting FILE-MANAGEMENT-SYSTEM-OS", "main")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        app = MainView()

        logger.info("Application window created successfully", "main")

        app.mainloop()

        logger.info("Application closed normally", "main")

    except Exception as e:
        logger.exception("Fatal error in main application", "main")
        raise


if __name__ == "__main__":
    main()

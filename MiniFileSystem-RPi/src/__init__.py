"""
MiniFileSystem Package
=======================
A lightweight file system simulator for educational purposes.

This package provides core functionality for:
- File management (create, read, write)
- Directory management (create, list, navigate)
- File search capabilities
- Command-line interface

Author: OS Lab Group 03
Date: October 2024
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "OS Lab Group 03"
__all__ = [
    'FileManager',
    'DirectoryManager',
    'SearchEngine',
    'CLIInterface'
]

from .file_manager import FileManager
from .directory_manager import DirectoryManager
from .search_engine import SearchEngine
from .cli_interface import CLIInterface

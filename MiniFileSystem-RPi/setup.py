# setup.py
from setuptools import setup, find_packages

setup(
    name='MiniFileSystem-RPi',
    version='1.0.0',
    author='OS Lab Group 03',
    description='A simple file system simulator for educational purposes.',
    packages=find_packages(),
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'minifs = src.cli_interface:main',
        ],
    },
)
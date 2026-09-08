from setuptools import setup, find_packages

setup(
    name="whisper-live",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "faster-whisper>=1.0.0",
        "sounddevice>=0.4.6",
        "numpy>=1.26.0",
        "click>=8.1.7",
        "rich>=13.7.0",
        "pyperclip>=1.8.2",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "whisper-live=whisper_live.cli.commands:cli",
        ],
    },
    python_requires=">=3.9",
)

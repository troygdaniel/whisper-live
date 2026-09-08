"""Configuration management for Whisper Live."""

import os
from pathlib import Path
import yaml


class Config:
    """Configuration manager for Whisper Live."""

    def __init__(self, config_path=None):
        if config_path is None:
            # Look for config.yaml in current directory or package directory
            if os.path.exists("config.yaml"):
                config_path = "config.yaml"
            else:
                # Default to package directory
                package_dir = Path(__file__).parent.parent
                config_path = package_dir / "config.yaml"

        self.config_path = Path(config_path)
        self.data = self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            # Return defaults if config file doesn't exist
            return self._default_config()

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _default_config(self):
        """Return default configuration."""
        return {
            'audio': {
                'sample_rate': 16000,
                'chunk_duration': 2.0,
            },
            'transcription': {
                'model': 'base',
                'language': None,
            },
            'output': {
                'file': {
                    'enabled': True,
                    'directory': './transcripts',
                    'format': 'txt',
                }
            }
        }

    def get(self, key, default=None):
        """Get configuration value using dot notation (e.g., 'audio.sample_rate')."""
        keys = key.split('.')
        value = self.data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    @property
    def sample_rate(self):
        return self.get('audio.sample_rate', 16000)

    @property
    def chunk_duration(self):
        return self.get('audio.chunk_duration', 2.0)

    @property
    def model(self):
        return self.get('transcription.model', 'base')

    @property
    def language(self):
        return self.get('transcription.language')

    @property
    def output_directory(self):
        return self.get('output.file.directory', './transcripts')

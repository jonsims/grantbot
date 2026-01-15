"""
Version Management System
Tracks version numbers for daily updates
"""

import os
import json
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class VersionManager:
    def __init__(self, version_file: str = "config/version.json"):
        self.version_file = version_file
        self.current_version = self._load_version()

    def _load_version(self) -> float:
        """Load current version from file"""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    return float(data.get('version', 0.3))
            except Exception as e:
                logger.error(f"Error loading version: {e}")
                return 0.3
        return 0.3

    def _save_version(self):
        """Save current version to file"""
        try:
            os.makedirs(os.path.dirname(self.version_file), exist_ok=True)
            with open(self.version_file, 'w') as f:
                json.dump({
                    'version': self.current_version,
                    'last_updated': str(__import__('datetime').datetime.now())
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving version: {e}")

    def get_version(self) -> float:
        """Get current version"""
        return self.current_version

    def get_version_string(self) -> str:
        """Get version as formatted string"""
        return f"v{self.current_version:.1f}"

    def increment_version(self, amount: float = 0.1):
        """Increment version by specified amount"""
        self.current_version = round(self.current_version + amount, 1)
        self._save_version()
        logger.info(f"Version incremented to {self.get_version_string()}")

    def set_version(self, version: float):
        """Set specific version"""
        self.current_version = version
        self._save_version()
        logger.info(f"Version set to {self.get_version_string()}")


if __name__ == "__main__":
    # Test version management
    vm = VersionManager()
    print(f"Current version: {vm.get_version_string()}")
    vm.increment_version()
    print(f"New version: {vm.get_version_string()}")
"""
RobiDev AI - Configuration
Central place for app-wide settings and file paths.
"""

import os

# Base directory of the whole project (RobiDev-AI/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Where conversation memory is stored
DATA_DIR = os.path.join(BASE_DIR, "data")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")

# Bot identity
BOT_NAME = "RobiDev AI"
VERSION = "v0.3"

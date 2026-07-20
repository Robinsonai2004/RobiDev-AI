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

# Weather API (v0.6 Step 4)
# Reads from an environment variable, never hardcoded. Set it in Termux with:
#   echo 'export OPENWEATHER_API_KEY="your_key_here"' >> ~/.bashrc && source ~/.bashrc
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

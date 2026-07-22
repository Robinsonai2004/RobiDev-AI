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
VERSION = "v0.6"

# Weather API (v0.6 Step 4)
# Reads from an environment variable, never hardcoded. Set it in Termux with:
#   echo 'export OPENWEATHER_API_KEY="your_key_here"' >> ~/.bashrc && source ~/.bashrc
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

# Web Search API (v0.6 Step 5)
# Reads from an environment variable, never hardcoded. Set it in Termux with:
#   echo 'export FIRECRAWL_API_KEY="fc-bef6b7083b3b420da514eb4009960d83"' >> ~/.bashrc && source ~/.bashrc
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")

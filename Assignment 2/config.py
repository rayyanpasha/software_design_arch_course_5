"""
Configuration file for CloudConnect application.
Centralized place for all configurable settings and constants.
"""

# --- Logging Configuration ---
LOG_DIRECTORY = "cloud_logs"
LOG_FILE = "cloudconnect.log"

# --- AppService Configuration Options ---
APPSERVICE_RUNTIMES = ["python", "nodejs", "dotnet"]
APPSERVICE_REGIONS = ["EastUS", "WestEurope", "CentralIndia"]
APPSERVICE_REPLICA_COUNTS = ["1", "2", "3"]

# --- StorageAccount Configuration Options ---
STORAGE_ENCRYPTION_OPTIONS = ["True", "False"]
STORAGE_MAX_SIZES_GB = ["10", "100", "1000"]

# --- CacheDB Configuration Options ---
CACHEDB_TTL_SECONDS = ["60", "300", "3600"]
CACHEDB_CAPACITIES_MB = ["100", "500", "1000"]
CACHEDB_EVICTION_POLICIES = ["LRU", "FIFO", "LFU"]

# --- Menu Configuration ---
MAIN_MENU_OPTIONS = {
    "1": "Create Resource",
    "2": "Start Resource",
    "3": "Stop Resource",
    "4": "Delete Resource",
    "5": "List All Resources",
    "6": "View Logs",
    "7": "Exit",
}
VALID_MENU_CHOICES = list(MAIN_MENU_OPTIONS.keys())

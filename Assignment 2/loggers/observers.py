# loggers/observers.py
"""
Concrete implementations of the Observer interface for logging.
"""
import datetime
import os
import sys
from patterns.observer import Observer

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class ConsoleLogger(Observer):
    """Logs messages to the console."""
    def update(self, resource_name: str, event: str, details: str):
        timestamp = datetime.datetime.now().strftime("%I:%M:%S %p")
        print(f"[CONSOLE LOG - {timestamp}] Event: {event} | {details}")

class FileLogger(Observer):
    """Logs messages to a file."""
    def __init__(self, log_directory=None, log_file=None):
        self.log_directory = log_directory or config.LOG_DIRECTORY
        self.log_file = log_file or config.LOG_FILE
        self.log_path = os.path.join(self.log_directory, self.log_file)
        
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

    def update(self, resource_name: str, event: str, details: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = (f"[{timestamp}] Resource: {resource_name} | "
                       f"Event: {event} | {details}\n")
        
        try:
            with open(self.log_path, "a") as f:
                f.write(log_message)
        except Exception as e:
            print(f"[FileLogger Error] Could not write to log: {e}")

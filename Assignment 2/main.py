# main.py
"""
CloudConnect - Main Entry Point
"""
import resources  # This import is crucial! It triggers the auto-registration
from cloud_manager import CloudManager

if __name__ == "__main__":
    manager = CloudManager()
    manager.main_loop()
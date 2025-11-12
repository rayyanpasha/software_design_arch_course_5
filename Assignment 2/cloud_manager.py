# cloud_manager.py
"""
The CloudManager class, which acts as the main controller/CLI.
"""
import os
from typing import Dict, List

from resource_factory import ResourceFactory
from resources.cloud_resource import CloudResource
from logging.observers import ConsoleLogger, FileLogger
from patterns.observer import Observer

class CloudManager:
    """The main application class that orchestrates the CLI and manages resources."""
    
    def __init__(self):
        self.resources: Dict[str, CloudResource] = {}
        
        # Create and hold the logger instances. This is a core
        # part of the Dependency Injection.
        self.console_logger = ConsoleLogger()
        self.file_logger = FileLogger(log_directory="cloud_logs")
        self.global_loggers: List[Observer] = [self.console_logger, self.file_logger]

    def _get_resource(self) -> CloudResource:
        """Helper to safely get a resource by name."""
        name = input("Enter resource name: ").strip()
        resource = self.resources.get(name)
        if not resource:
            print(f"Error: Resource '{name}' not found.")
            return None
        return resource

    def _select_from_options(self, prompt: str, options: List[str]) -> str:
        """Helper for a simple, validated menu."""
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            choice = input(f"Choice (1-{len(options)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1]
            print("Invalid choice. Please try again.")

    def handle_create_resource(self):
        """Guides the user through creating a new resource."""
        print("\n--- Create New Resource ---")
        
        # This is extensible. The factory's registry is the single
        # source of truth for available resource types.
        available_types = list(ResourceFactory.get_registered_types())
        if not available_types:
            print("Error: No resource types have been registered.")
            return
            
        type_name = self._select_from_options(
            "Select resource type:",
            available_types
        )
        
        name = input("Enter a unique name for this resource: ").strip()
        if not name:
            print("Error: Name cannot be empty.")
            return
        if name in self.resources:
            print(f"Error: A resource with name '{name}' already exists.")
            return
            
        config = {}
        # --- Configuration logic as per requirements ---
        if type_name == "AppService":
            config["runtime"] = self._select_from_options(
                "Select runtime:", ["python", "nodejs", "dotnet"]
            )
            config["region"] = self._select_from_options(
                "Select region:", ["EastUS", "WestEurope", "CentralIndia"]
            )
            config["replica_count"] = int(self._select_from_options(
                "Select replica count:", ["1", "2", "3"]
            ))
        elif type_name == "StorageAccount":
            config["encryption_enabled"] = self._select_from_options(
                "Enable encryption?", ["True", "False"]
            ) == "True"
            config["access_key"] = "key-" + os.urandom(8).hex() # Generate dummy key
            config["max_size_gb"] = int(self._select_from_options(
                "Select max size (GB):", ["10", "100", "1000"]
            ))
        elif type_name == "CacheDB":
            config["ttl_seconds"] = int(self._select_from_options(
                "Select TTL (seconds):", ["60", "300", "3600"]
            ))
            config["capacity_mb"] = int(self._select_from_options(
                "Select capacity (MB):", ["100", "500", "1000"]
            ))
            config["eviction_policy"] = self._select_from_options(
                "Select eviction policy:", ["LRU", "FIFO", "LFU"]
            )
        
        try:
            # --- Dependency Injection in action ---
            # We pass the loggers to the factory. The factory
            # passes them to the resource's constructor.
            resource = ResourceFactory.create_resource(
                type_name=type_name,
                name=name,
                config=config,
                observers=self.global_loggers
            )
            self.resources[name] = resource
            print(f"\nSuccess! {type_name} '{name}' created.")
        except ValueError as e:
            print(f"Error: {e}")

    def handle_start_resource(self):
        print("\n--- Start Resource ---")
        resource = self._get_resource()
        if resource:
            # We "program to the interface." We just call start().
            # The resource's internal State object handles all logic.
            resource.start() 

    def handle_stop_resource(self):
        print("\n--- Stop Resource ---")
        resource = self._get_resource()
        if resource:
            resource.stop()

    def handle_delete_resource(self):
        print("\n--- Delete Resource ---")
        resource = self._get_resource()
        if resource:
            resource.delete()

    def handle_view_logs(self):
        """A simple log viewer (for the file log)."""
        print("\n--- Viewing Logs (from cloud_logs/cloudconnect.log) ---")
        log_file = os.path.join(self.file_logger.log_directory, self.file_logger.log_file)
        if not os.path.exists(log_file):
            print("No log file found. Perform some actions first.")
            return
            
        try:
            with open(log_file, "r") as f:
                print(f.read())
        except Exception as e:
            print(f"Error reading log file: {e}")

    def handle_list_resources(self):
        """Shows the status of all current resources."""
        print("\n--- Current Resources ---")
        if not self.resources:
            print("No resources created yet.")
            return
            
        for name, resource in self.resources.items():
            print(f"- Name: {name}")
            print(f"  Type: {resource.__class__.__name__}")
            print(f"  Status: {resource.get_status()}")
            print(f"  Details: {resource.get_details()}")
            print("-" * 20)

    def main_loop(self):
        """The main menu-driven interface."""
        print("Welcome to CloudConnect, the Cloud Resource Manager")
        while True:
            print("\n--- Main Menu ---")
            print("1. Create Resource")
            print("2. Start Resource")
            print("3. Stop Resource")
            print("4. Delete Resource")
            print("5. List All Resources")
            print("6. View Logs")
            print("7. Exit")
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == '1':
                self.handle_create_resource()
            elif choice == '2':
                self.handle_start_resource()
            elif choice == '3':
                self.handle_stop_resource()
            elif choice == '4':
                self.handle_delete_resource()
            elif choice == '5':
                self.handle_list_resources()
            elif choice == '6':
                self.handle_view_logs()
            elif choice == '7':
                print("Exiting CloudConnect. Goodbye!")
                break
            else:
                print("Invalid choice. Please select from 1-7.")
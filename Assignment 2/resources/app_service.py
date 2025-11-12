# resources/app_service.py
"""Concrete Implementation for AppService."""
from .cloud_resource import CloudResource
from resource_factory import ResourceFactory

class AppService(CloudResource):
    def get_details(self) -> str:
        return (f"Type: AppService, "
                f"Runtime: {self.config.get('runtime')}, "
                f"Region: {self.config.get('region')}")

# --- Auto-registration ---
# This line "plugs in" the AppService to the factory.
ResourceFactory.register_resource("AppService", AppService)
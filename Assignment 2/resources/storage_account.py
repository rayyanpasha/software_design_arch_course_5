# resources/storage_account.py
"""Concrete Implementation for StorageAccount."""
from .cloud_resource import CloudResource
from resource_factory import ResourceFactory

class StorageAccount(CloudResource):
    def get_details(self) -> str:
        return (f"Type: StorageAccount, "
                f"Encryption: {self.config.get('encryption_enabled')}, "
                f"MaxSize: {self.config.get('max_size_gb')}GB")

# --- Auto-registration ---
ResourceFactory.register_resource("StorageAccount", StorageAccount)
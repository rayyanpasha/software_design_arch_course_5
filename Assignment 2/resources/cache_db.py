# resources/cache_db.py
"""Concrete Implementation for CacheDB."""
from .cloud_resource import CloudResource
from resource_factory import ResourceFactory

class CacheDB(CloudResource):
    def get_details(self) -> str:
        return (f"Type: CacheDB, "
                f"Policy: {self.config.get('eviction_policy')}, "
                f"Capacity: {self.config.get('capacity_mb')}MB")

# --- Auto-registration ---
ResourceFactory.register_resource("CacheDB", CacheDB)
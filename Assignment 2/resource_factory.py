# resource_factory.py
"""
Implements the Factory Pattern for creating resources.
"""
from typing import Dict, Type, List, Any
from patterns.observer import Observer
# We need to import CloudResource for type hinting, but
# we must use 'import ...' to avoid circular imports.
import resources.cloud_resource 

class ResourceFactory:
    """The Factory for creating all resource types."""
    
    # The "registry" you required
    _registry: Dict[str, Type['resources.cloud_resource.CloudResource']] = {}

    @classmethod
    def register_resource(cls, type_name: str, resource_class: Type['resources.cloud_resource.CloudResource']):
        """Class method to register a new resource type."""
        cls._registry[type_name] = resource_class

    @classmethod
    def create_resource(cls, type_name: str, name: str, config: Dict[str, Any], observers: List[Observer]) -> 'resources.cloud_resource.CloudResource':
        """
        Factory method to create a resource.
        It passes the observers to the constructor.
        """
        resource_class = cls._registry.get(type_name)
        if not resource_class:
            raise ValueError(f"Unknown resource type: {type_name}")
        
        # This calls the CloudResource constructor, which logs the creation
        return resource_class(name=name, config=config, observers=observers)

    @classmethod
    def get_registered_types(cls) -> List[str]:
        """Returns a list of all registered resource type names."""
        return list(cls._registry.keys())
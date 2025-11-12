# patterns/state.py
"""
Interfaces and concrete classes for the State Pattern.
"""
import abc
from typing import TYPE_CHECKING

# This is a common trick to avoid circular imports.
# The CloudResource class is only needed for type hinting.
if TYPE_CHECKING:
    from resources.cloud_resource import CloudResource

class ResourceState(metaclass=abc.ABCMeta):
    """
    Interface for the State pattern. Defines the lifecycle methods.
    Methods return the *new* state the resource should transition to.
    """
    @abc.abstractmethod
    def start(self, context: 'CloudResource') -> 'ResourceState':
        pass

    @abc.abstractmethod
    def stop(self, context: 'CloudResource') -> 'ResourceState':
        pass

    @abc.abstractmethod
    def delete(self, context: 'CloudResource') -> 'ResourceState':
        pass

    def __str__(self):
        # Returns the class name without "State" (e.g., "Created")
        return self.__class__.__name__.replace("State", "")

# --- Concrete State Implementations ---

class CreatedState(ResourceState):
    """The state for a newly created, non-running resource."""
    def start(self, context: 'CloudResource') -> ResourceState:
        context.notify("Started", f"Resource '{context.name}' started. {context.get_details()}")
        return StartedState()  # Return the new state

    def stop(self, context: 'CloudResource') -> ResourceState:
        context.notify("Error", "Cannot stop. Resource is not running.")
        return self  # No state change

    def delete(self, context: 'CloudResource') -> ResourceState:
        context.notify("Deleted", f"Resource '{context.name}' marked as deleted.")
        return DeletedState()

class StartedState(ResourceState):
    """The state for a running resource."""
    def start(self, context: 'CloudResource') -> ResourceState:
        context.notify("Error", "Cannot start. Resource is already running.")
        return self

    def stop(self, context: 'CloudResource') -> ResourceState:
        context.notify("Stopped", f"Resource '{context.name}' stopped successfully.")
        return StoppedState()

    def delete(self, context: 'CloudResource') -> ResourceState:
        context.notify("Error", "Cannot delete. Resource must be stopped first.")
        return self

class StoppedState(ResourceState):
    """The state for a resource that has been stopped."""
    def start(self, context: 'CloudResource') -> ResourceState:
        context.notify("Started", f"Resource '{context.name}' restarted. {context.get_details()}")
        return StartedState()

    def stop(self, context: 'CloudResource') -> ResourceState:
        context.notify("Error", "Cannot stop. Resource is already stopped.")
        return self

    def delete(self, context: 'CloudResource') -> ResourceState:
        context.notify("Deleted", f"Resource '{context.name}' marked as deleted.")
        return DeletedState()

class DeletedState(ResourceState):
    """The final 'soft delete' state. Resource is non-functional."""
    def start(self, context: 'CloudResource') -> ResourceState:
        context.notify("Error", "Cannot start. Resource has been deleted.")
        return self

    def stop(self, context: 'CloudResource') -> ResourceState:
        context.notify("Error", "Cannot stop. Resource has been deleted.")
        return self

    def delete(self, context: 'CloudResource') -> ResourceState:
        context.notify("Error", "Resource is already deleted.")
        return self
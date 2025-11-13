# resources/cloud_resource.py
"""
Abstract Base Class for all CloudResources.
"""
import abc
from typing import List, Dict, Any
from patterns.observer import Observer
from patterns.state import ResourceState, CreatedState

class CloudResource(metaclass=abc.ABCMeta):
    """
    Abstract Base Class for all resources.
    Acts as the 'Observable' for the Observer pattern.
    Acts as the 'Context' for the State pattern.
    """
    def __init__(self, name: str, config: Dict[str, Any], observers: List[Observer]):
        self.name = name
        self.config = config
        self._observers = observers
        # We must set the state *before* notifying,
        # otherwise we can't get a status.
        self._state = CreatedState()
        
        # Immediately log creation (This solves the "how to log creation" problem)
        self.notify("Created", f"Resource '{self.name}' created. {self.get_details()}")

    def notify(self, event: str, details: str):
        """Notify all attached observers."""
        for observer in self._observers:
            observer.update(self.name, event, details)

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
            
    def _set_state(self, new_state: ResourceState):
        """Private method to set the state."""
        self._state = new_state

    # --- State-delegated Methods ---
    
    def start(self):
        """Delegates the 'start' action to the current state object."""
        # The state method performs the action and returns the *new* state.
        # The resource itself manages its own state variable.
        new_state = self._state.start(self)
        self._set_state(new_state)

    def stop(self):
        """Delegates the 'stop' action to the current state object."""
        new_state = self._state.stop(self)
        self._set_state(new_state)

    def delete(self):
        """Delegates the 'delete' action to the current state object."""
        new_state = self._state.delete(self)
        self._set_state(new_state)

    @abc.abstractmethod
    def get_details(self) -> str:
        """Forces subclasses to implement a details method."""
        pass
        
    def get_status(self) -> str:
        """Helper to get the current state's name."""
        return str(self._state)
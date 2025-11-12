# patterns/observer.py
"""
Interfaces for the Observer Pattern.
"""
import abc

class Observer(metaclass=abc.ABCMeta):
    """
    Interface for the Observer pattern. Requires an update method.
    """
    @abc.abstractmethod
    def update(self, resource_name: str, event: str, details: str):
        pass
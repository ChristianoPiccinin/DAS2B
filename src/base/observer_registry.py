"""
Global observer registry for Azure Functions triggers.

Allows observers to be registered once at application startup and
automatically attached to all new trigger instances.
"""

from typing import List
from .trigger_observer import Observer

_global_observers: List[Observer] = []


def register_global_observer(observer: Observer) -> None:
    """
    Register an observer globally.

    This observer will be automatically attached to all BaseTrigger instances
    created after registration. Useful for attaching logging, metrics, and
    error handling observers at application startup.

    Args:
        observer: Observer instance to register globally
    """
    if observer not in _global_observers:
        _global_observers.append(observer)


def unregister_global_observer(observer: Observer) -> None:
    """
    Unregister a global observer.

    Args:
        observer: Observer instance to remove from global registry
    """
    if observer in _global_observers:
        _global_observers.remove(observer)


def get_global_observers() -> List[Observer]:
    """
    Get a copy of the current global observers list.

    Returns:
        List of all currently registered global observers
    """
    return _global_observers.copy()


def clear_global_observers() -> None:
    """
    Clear all global observers.

    Useful for testing to reset state between test runs.
    """
    _global_observers.clear()

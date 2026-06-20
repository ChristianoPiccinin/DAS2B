"""Base module for Azure Functions trigger infrastructure."""

from .trigger_observer import (
    Observer,
    BaseTrigger,
    TriggerStartEvent,
    TriggerSuccessEvent,
    TriggerFailureEvent,
    TriggerCompleteEvent,
)
from .observer_registry import (
    register_global_observer,
    unregister_global_observer,
    get_global_observers,
    clear_global_observers,
)

__all__ = [
    'Observer',
    'BaseTrigger',
    'TriggerStartEvent',
    'TriggerSuccessEvent',
    'TriggerFailureEvent',
    'TriggerCompleteEvent',
    'register_global_observer',
    'unregister_global_observer',
    'get_global_observers',
    'clear_global_observers',
]

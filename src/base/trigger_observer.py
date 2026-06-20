"""
Observer pattern implementation for Azure Functions trigger lifecycle.

Provides abstract Observer base class, event dataclasses, and BaseTrigger class
for attaching observers to trigger execution lifecycle.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TriggerStartEvent:
    """Event emitted when trigger execution starts."""
    trigger_name: str
    timestamp: datetime
    execution_id: str


@dataclass(frozen=True)
class TriggerSuccessEvent:
    """Event emitted after successful extraction and upload."""
    trigger_name: str
    duration_seconds: float
    rows_processed: int
    execution_id: str


@dataclass(frozen=True)
class TriggerFailureEvent:
    """Event emitted when an exception occurs during trigger execution."""
    trigger_name: str
    duration_seconds: float
    exception: Exception
    execution_id: str


@dataclass(frozen=True)
class TriggerCompleteEvent:
    """Event emitted after all processing is complete (finally block)."""
    trigger_name: str
    execution_id: str


class Observer(ABC):
    """
    Abstract base class for trigger lifecycle observers.

    Observers can subscribe to trigger events and react to them without
    coupling to individual trigger implementations.

    Subclasses should override lifecycle methods to implement custom behavior.
    All methods have default no-op implementations.
    """

    def on_start(self, event: TriggerStartEvent) -> None:
        """
        Called when trigger execution begins.

        Args:
            event: TriggerStartEvent with trigger_name, timestamp, execution_id
        """
        pass

    def on_success(self, event: TriggerSuccessEvent) -> None:
        """
        Called after successful extraction and blob storage upload.

        Args:
            event: TriggerSuccessEvent with duration, row count, execution_id
        """
        pass

    def on_failure(self, event: TriggerFailureEvent) -> None:
        """
        Called when an exception occurs during execution.

        Args:
            event: TriggerFailureEvent with exception, duration, execution_id
        """
        pass

    def on_complete(self, event: TriggerCompleteEvent) -> None:
        """
        Called after all processing (finally block), always executed.

        Args:
            event: TriggerCompleteEvent with trigger_name, execution_id
        """
        pass


class BaseTrigger:
    """
    Base class for extraction triggers with observer support.

    Provides lifecycle hooks and observer registration/management.
    Triggers inherit from this class to gain observer functionality.

    Observers are called synchronously in registration order.
    Observer failures are caught, logged, and do not crash the trigger.
    """

    def __init__(self, trigger_name: str, observers: Optional[List[Observer]] = None):
        """
        Initialize trigger with optional observers.

        Automatically attaches global observers registered via observer_registry.

        Args:
            trigger_name: Name identifier for this trigger
            observers: List of Observer instances to attach (optional)
        """
        self.trigger_name = trigger_name
        self._observers: List[Observer] = []

        # Attach explicitly provided observers first
        if observers:
            self._observers.extend(observers)

        # Attach global observers from registry (lazy import to avoid circular dependency)
        try:
            from . import observer_registry
            global_observers = observer_registry.get_global_observers()
            self._observers.extend(global_observers)
        except ImportError:
            # observer_registry module not available, skip global observers
            pass

    def register_observer(self, observer: Observer) -> None:
        """
        Register an observer to receive lifecycle events.

        Args:
            observer: Observer instance to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer: Observer) -> None:
        """
        Unregister an observer from this trigger.

        Args:
            observer: Observer instance to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, lifecycle_event: str, event_data: object) -> None:
        """
        Publish a lifecycle event to all registered observers.

        Calls the corresponding observer method (on_start, on_success, etc.)
        for each observer in registration order. Observer exceptions are
        caught, logged, and isolated — a failing observer does not prevent
        other observers from being called or the trigger from completing.

        Args:
            lifecycle_event: Event type name ('start', 'success', 'failure', 'complete')
            event_data: Event payload (TriggerStartEvent, etc.)
        """
        method_name = f'on_{lifecycle_event}'

        for observer in self._observers:
            try:
                method = getattr(observer, method_name, None)
                if method and callable(method):
                    method(event_data)
            except Exception as e:
                logger.error(
                    f"Observer error in {observer.__class__.__name__}.{method_name}: {e}",
                    exc_info=True
                )

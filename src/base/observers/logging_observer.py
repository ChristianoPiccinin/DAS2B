"""Logging observer for trigger lifecycle events."""

import logging
from ..trigger_observer import (
    Observer,
    TriggerStartEvent,
    TriggerSuccessEvent,
    TriggerFailureEvent,
    TriggerCompleteEvent,
)

logger = logging.getLogger(__name__)


class LoggingObserver(Observer):
    """
    Observer that logs trigger lifecycle events.

    Logs at INFO level for normal events, ERROR level for failures,
    and DEBUG level for cleanup.
    """

    def on_start(self, event: TriggerStartEvent) -> None:
        """Log trigger start."""
        logger.info(
            f"Trigger {event.trigger_name} started (execution_id={event.execution_id})"
        )

    def on_success(self, event: TriggerSuccessEvent) -> None:
        """Log successful trigger completion with metrics."""
        logger.info(
            f"Trigger {event.trigger_name} completed in {event.duration_seconds:.2f}s, "
            f"{event.rows_processed} rows"
        )

    def on_failure(self, event: TriggerFailureEvent) -> None:
        """Log trigger failure with exception details."""
        logger.error(
            f"Trigger {event.trigger_name} failed after {event.duration_seconds:.2f}s: "
            f"{event.exception.__class__.__name__}: {event.exception}",
            exc_info=event.exception
        )

    def on_complete(self, event: TriggerCompleteEvent) -> None:
        """Log trigger cleanup completion."""
        logger.debug(
            f"Trigger {event.trigger_name} cleanup complete (execution_id={event.execution_id})"
        )

"""Error observer for enhanced diagnostic logging on trigger failures."""

import logging
from ..trigger_observer import (
    Observer,
    TriggerFailureEvent,
)

logger = logging.getLogger(__name__)


class ErrorObserver(Observer):
    """
    Observer that logs detailed diagnostic information on trigger failures.

    Provides enhanced context to aid debugging when triggers encounter errors.
    """

    def on_failure(self, event: TriggerFailureEvent) -> None:
        """Log detailed diagnostic context on failure."""
        logger.error(
            f"Trigger failure diagnostics: trigger={event.trigger_name}, "
            f"execution_id={event.execution_id}, "
            f"error_type={event.exception.__class__.__name__}, "
            f"duration={event.duration_seconds:.2f}s"
        )

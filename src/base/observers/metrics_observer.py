"""Metrics observer for collecting trigger execution metrics."""

from ..trigger_observer import (
    Observer,
    TriggerStartEvent,
    TriggerSuccessEvent,
    TriggerFailureEvent,
    TriggerCompleteEvent,
)


class MetricsObserver(Observer):
    """
    Observer that collects trigger execution metrics.

    Records metric events internally (counters, timings, etc.)
    without emitting logs. Provides integration point for backend
    metrics systems (Application Insights, Datadog, etc.).
    """

    def __init__(self):
        """Initialize metrics observer with internal counters."""
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.total_rows_processed = 0

    def on_start(self, event: TriggerStartEvent) -> None:
        """Record trigger start time for later latency calculation."""
        # Timestamp is already in the event; no action needed here
        # Subclasses or backends can extract timing data
        pass

    def on_success(self, event: TriggerSuccessEvent) -> None:
        """Increment success metrics and accumulate row counts."""
        self.successful_executions += 1
        self.total_rows_processed += event.rows_processed

    def on_failure(self, event: TriggerFailureEvent) -> None:
        """Increment failure counter."""
        self.failed_executions += 1

    def on_complete(self, event: TriggerCompleteEvent) -> None:
        """Finalize execution metrics."""
        self.total_executions += 1

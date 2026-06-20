"""
Unit tests for observer lifecycle integration with triggers.

Tests verify that trigger lifecycle methods call observer methods in the correct order
with correct event payloads, and that observer failures are isolated from trigger execution.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, call, patch

from base import (
    BaseTrigger,
    Observer,
    TriggerStartEvent,
    TriggerSuccessEvent,
    TriggerFailureEvent,
    TriggerCompleteEvent,
)


class MockObserver(Observer):
    """Mock observer that records all method calls."""

    def __init__(self):
        self.calls = []

    def on_start(self, event: TriggerStartEvent) -> None:
        self.calls.append(('start', event))

    def on_success(self, event: TriggerSuccessEvent) -> None:
        self.calls.append(('success', event))

    def on_failure(self, event: TriggerFailureEvent) -> None:
        self.calls.append(('failure', event))

    def on_complete(self, event: TriggerCompleteEvent) -> None:
        self.calls.append(('complete', event))


class FailingObserver(Observer):
    """Observer that raises an exception to test error isolation."""

    def on_success(self, event: TriggerSuccessEvent) -> None:
        raise ValueError("Intentional observer failure for testing")


class TestObserverLifecycle(unittest.TestCase):
    """Test observer lifecycle integration."""

    def test_observer_methods_called_in_order_on_success(self):
        """Verify observers are called in correct order on successful trigger."""
        obs1 = MockObserver()
        obs2 = MockObserver()

        trigger = BaseTrigger('test_trigger', observers=[obs1, obs2])

        # Simulate successful trigger execution
        trigger._notify_observers('start', TriggerStartEvent(
            trigger_name='test_trigger',
            timestamp=datetime.now(),
            execution_id='123'
        ))
        trigger._notify_observers('success', TriggerSuccessEvent(
            trigger_name='test_trigger',
            duration_seconds=1.5,
            rows_processed=100,
            execution_id='123'
        ))
        trigger._notify_observers('complete', TriggerCompleteEvent(
            trigger_name='test_trigger',
            execution_id='123'
        ))

        # Verify observers called in order
        self.assertEqual(len(obs1.calls), 3)
        self.assertEqual(obs1.calls[0][0], 'start')
        self.assertEqual(obs1.calls[1][0], 'success')
        self.assertEqual(obs1.calls[2][0], 'complete')

        self.assertEqual(len(obs2.calls), 3)
        self.assertEqual(obs2.calls[0][0], 'start')
        self.assertEqual(obs2.calls[1][0], 'success')
        self.assertEqual(obs2.calls[2][0], 'complete')

    def test_failure_and_complete_events_on_exception(self):
        """Verify on_failure and on_complete are called on trigger exception."""
        obs = MockObserver()
        trigger = BaseTrigger('test_trigger', observers=[obs])

        trigger._notify_observers('start', TriggerStartEvent(
            trigger_name='test_trigger',
            timestamp=datetime.now(),
            execution_id='456'
        ))

        exception = RuntimeError('Database error')
        trigger._notify_observers('failure', TriggerFailureEvent(
            trigger_name='test_trigger',
            duration_seconds=0.5,
            exception=exception,
            execution_id='456'
        ))

        trigger._notify_observers('complete', TriggerCompleteEvent(
            trigger_name='test_trigger',
            execution_id='456'
        ))

        # Verify failure was called
        self.assertEqual(len(obs.calls), 3)
        self.assertEqual(obs.calls[1][0], 'failure')
        self.assertEqual(obs.calls[1][1].exception, exception)

    def test_observer_exception_isolation(self):
        """Verify observer exceptions don't crash trigger execution."""
        failing_obs = FailingObserver()
        good_obs = MockObserver()

        trigger = BaseTrigger('test_trigger', observers=[failing_obs, good_obs])

        # This should not raise even though failing_obs.on_success raises
        with patch('base.trigger_observer.logger') as mock_logger:
            trigger._notify_observers('success', TriggerSuccessEvent(
                trigger_name='test_trigger',
                duration_seconds=1.0,
                rows_processed=50,
                execution_id='789'
            ))

            # Verify error was logged
            mock_logger.error.assert_called_once()

        # Verify good observer was still called
        self.assertEqual(len(good_obs.calls), 1)
        self.assertEqual(good_obs.calls[0][0], 'success')

    def test_multiple_observers_registration_order(self):
        """Verify multiple observers are called in registration order."""
        obs1 = MockObserver()
        obs2 = MockObserver()

        trigger = BaseTrigger('test_trigger')
        trigger.register_observer(obs1)
        trigger.register_observer(obs2)

        event = TriggerStartEvent(
            trigger_name='test_trigger',
            timestamp=datetime.now(),
            execution_id='xyz'
        )
        trigger._notify_observers('start', event)

        # obs1 should be called first, then obs2
        self.assertEqual(obs1.calls[0], ('start', event))
        self.assertEqual(obs2.calls[0], ('start', event))

    def test_event_payload_accuracy(self):
        """Verify event payloads contain accurate data."""
        obs = MockObserver()
        trigger = BaseTrigger('extract_test', observers=[obs])

        # Test success event with specific metrics
        success_event = TriggerSuccessEvent(
            trigger_name='extract_test',
            duration_seconds=2.345,
            rows_processed=5000,
            execution_id='metrics-123'
        )
        trigger._notify_observers('success', success_event)

        # Verify payload data is correct
        received_event = obs.calls[0][1]
        self.assertEqual(received_event.trigger_name, 'extract_test')
        self.assertAlmostEqual(received_event.duration_seconds, 2.345, places=3)
        self.assertEqual(received_event.rows_processed, 5000)
        self.assertEqual(received_event.execution_id, 'metrics-123')

    def test_observer_unregistration(self):
        """Verify unregistered observers are not called."""
        obs1 = MockObserver()
        obs2 = MockObserver()

        trigger = BaseTrigger('test_trigger', observers=[obs1, obs2])
        trigger.unregister_observer(obs1)

        trigger._notify_observers('start', TriggerStartEvent(
            trigger_name='test_trigger',
            timestamp=datetime.now(),
            execution_id='test'
        ))

        # obs1 should not be called
        self.assertEqual(len(obs1.calls), 0)
        # obs2 should be called
        self.assertEqual(len(obs2.calls), 1)


if __name__ == '__main__':
    unittest.main()

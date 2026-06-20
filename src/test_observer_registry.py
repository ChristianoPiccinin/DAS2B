"""
Unit tests for global observer registry functionality.

Tests verify that observers can be registered globally and automatically
attached to BaseTrigger instances.
"""

import unittest
from base import (
    BaseTrigger,
    Observer,
    TriggerStartEvent,
    clear_global_observers,
    register_global_observer,
    unregister_global_observer,
    get_global_observers,
)
from datetime import datetime


class SimpleObserver(Observer):
    """Simple test observer."""

    def __init__(self, name):
        self.name = name
        self.events = []

    def on_start(self, event: TriggerStartEvent) -> None:
        self.events.append(('start', event.trigger_name))


class TestObserverRegistry(unittest.TestCase):
    """Test global observer registry."""

    def setUp(self):
        """Clear global observers before each test."""
        clear_global_observers()

    def tearDown(self):
        """Clear global observers after each test."""
        clear_global_observers()

    def test_register_global_observer(self):
        """Verify observer can be registered globally."""
        obs = SimpleObserver('test')
        register_global_observer(obs)

        global_obs = get_global_observers()
        self.assertIn(obs, global_obs)
        self.assertEqual(len(global_obs), 1)

    def test_global_observer_attached_to_new_trigger(self):
        """Verify global observer is attached to newly created triggers."""
        obs = SimpleObserver('global')
        register_global_observer(obs)

        # Create trigger after registering observer
        trigger = BaseTrigger('test_trigger')

        # Trigger should have the observer
        trigger._notify_observers('start', TriggerStartEvent(
            trigger_name='test_trigger',
            timestamp=datetime.now(),
            execution_id='123'
        ))

        # Observer should have received the event
        self.assertEqual(len(obs.events), 1)
        self.assertEqual(obs.events[0][0], 'start')

    def test_multiple_global_observers(self):
        """Verify multiple global observers coexist."""
        obs1 = SimpleObserver('obs1')
        obs2 = SimpleObserver('obs2')
        obs3 = SimpleObserver('obs3')

        register_global_observer(obs1)
        register_global_observer(obs2)
        register_global_observer(obs3)

        global_obs = get_global_observers()
        self.assertEqual(len(global_obs), 3)
        self.assertIn(obs1, global_obs)
        self.assertIn(obs2, global_obs)
        self.assertIn(obs3, global_obs)

    def test_unregister_global_observer(self):
        """Verify global observer can be unregistered."""
        obs1 = SimpleObserver('obs1')
        obs2 = SimpleObserver('obs2')

        register_global_observer(obs1)
        register_global_observer(obs2)

        unregister_global_observer(obs1)

        global_obs = get_global_observers()
        self.assertEqual(len(global_obs), 1)
        self.assertNotIn(obs1, global_obs)
        self.assertIn(obs2, global_obs)

    def test_clear_global_observers(self):
        """Verify all global observers can be cleared."""
        register_global_observer(SimpleObserver('obs1'))
        register_global_observer(SimpleObserver('obs2'))

        global_obs = get_global_observers()
        self.assertEqual(len(global_obs), 2)

        clear_global_observers()

        global_obs = get_global_observers()
        self.assertEqual(len(global_obs), 0)


if __name__ == '__main__':
    unittest.main()

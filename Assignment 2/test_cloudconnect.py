import unittest
from unittest.mock import Mock, patch

# --- Import all the classes we need to test
from resource_factory import ResourceFactory
from resources.cloud_resource import CloudResource
from resources.app_service import AppService
from resources.storage_account import StorageAccount
from resources.cache_db import CacheDB
from patterns.state import CreatedState, StartedState, StoppedState, DeletedState
from patterns.observer import Observer

class TestFactoryAndLogging(unittest.TestCase):
    """
    Tests the Factory, resource creation, and the Observer logging.
    """
    
    def setUp(self):
        # This runs before each test
        self.mock_logger = Mock(spec=Observer)
        self.observers = [self.mock_logger]

    def test_factory_can_create_all_types(self):
        """Test that the factory registry is working and can create resources."""
        
        # 1. Create an AppService
        app = ResourceFactory.create_resource(
            "AppService", "test-app", {}, self.observers
        )
        self.assertIsInstance(app, AppService)

        # 2. Create a StorageAccount
        storage = ResourceFactory.create_resource(
            "StorageAccount", "test-storage", {}, self.observers
        )
        self.assertIsInstance(storage, StorageAccount)

        # 3. Create a CacheDB
        cache = ResourceFactory.create_resource(
            "CacheDB", "test-cache", {}, self.observers
        )
        self.assertIsInstance(cache, CacheDB)

    def test_factory_raises_error_for_unknown_type(self):
        """Test that the factory gracefully fails for an unregistered type."""
        
        # Use assertRaises as a context manager to catch the expected error
        with self.assertRaises(ValueError):
            ResourceFactory.create_resource(
                "Database", "test-db", {}, self.observers
            )

    def test_resource_logs_creation_on_init(self):
        """
        Crucial test: Verifies that the resource constructor calls notify()
        and logs its own creation (Fix #1 from our refinement).
        """
        self.mock_logger.reset_mock() # Clear any previous calls
        
        resource = ResourceFactory.create_resource(
            "AppService", "test-app", {"region": "EastUS"}, self.observers
        )
        
        # Check that 'update' was called exactly ONCE
        self.mock_logger.update.assert_called_once()
        
        # Check the arguments of that one call
        call_args = self.mock_logger.update.call_args[0]
        self.assertEqual(call_args[0], "test-app")  # resource_name
        self.assertEqual(call_args[1], "Created")   # event
        self.assertIn("AppService", call_args[2])   # details
        self.assertIn("EastUS", call_args[2])       # details

    def test_resource_notify_calls_all_observers(self):
        """Test that notify() loops through all observers."""
        mock_logger_1 = Mock(spec=Observer)
        mock_logger_2 = Mock(spec=Observer)
        observers = [mock_logger_1, mock_logger_2]
        
        resource = ResourceFactory.create_resource(
            "AppService", "test-app", {}, observers
        )
        
        # Reset mocks to ignore the "Created" log
        mock_logger_1.reset_mock()
        mock_logger_2.reset_mock()

        # Act
        resource.notify("TestEvent", "TestDetails")

        # Assert
        mock_logger_1.update.assert_called_once_with("test-app", "TestEvent", "TestDetails")
        mock_logger_2.update.assert_called_once_with("test-app", "TestEvent", "TestDetails")


class TestResourceLifecycle(unittest.TestCase):
    """
    Tests the State Pattern and all valid/invalid lifecycle transitions.
    """
    
    def setUp(self):
        # This runs before each test
        self.mock_logger = Mock(spec=Observer)
        self.observers = [self.mock_logger]
        self.resource = ResourceFactory.create_resource(
            "AppService", "test-app", {"region": "EastUS"}, self.observers
        )
        # Reset the mock after creation, so we can test *new* actions
        self.mock_logger.reset_mock()

    def test_initial_state_is_created(self):
        """Test that a new resource is in the 'Created' state."""
        self.assertEqual(self.resource.get_status(), "Created")

    def test_created_to_started_is_valid(self):
        """Test: Created -> Start() -> Started"""
        self.resource.start()
        self.assertEqual(self.resource.get_status(), "Started")
        # Check that it logged the "Started" event
        self.mock_logger.update.assert_called_with("test-app", "Started", unittest.mock.ANY)

    def test_created_to_stopped_is_invalid(self):
        """Test: Created -> Stop() -> Created"""
        self.resource.stop()
        self.assertEqual(self.resource.get_status(), "Created") # State should not change
        # Check that it logged an "Error"
        self.mock_logger.update.assert_called_with("test-app", "Error", "Cannot stop. Resource is not running.")

    def test_started_to_deleted_is_invalid(self):
        """Test: Started -> Delete() -> Started"""
        self.resource.start() # Get to "Started" state
        self.mock_logger.reset_mock() # Clear the "Started" log
        
        # Act
        self.resource.delete()
        
        # Assert
        self.assertEqual(self.resource.get_status(), "Started") # State should not change
        self.mock_logger.update.assert_called_with("test-app", "Error", "Cannot delete. Resource must be stopped first.")

    def test_full_valid_lifecycle_flow(self):
        """Test the full happy path: Created -> Started -> Stopped -> Deleted"""
        
        # 1. Created -> Started
        self.resource.start()
        self.assertEqual(self.resource.get_status(), "Started")
        
        # 2. Started -> Stopped
        self.resource.stop()
        self.assertEqual(self.resource.get_status(), "Stopped")

        # 3. Stopped -> Deleted
        self.resource.delete()
        self.assertEqual(self.resource.get_status(), "Deleted")

    def test_stopped_to_started_is_valid(self):
        """Test (Restart): Stopped -> Start() -> Started"""
        self.resource.start() # Started
        self.resource.stop()  # Stopped
        self.mock_logger.reset_mock() # Clear logs
        
        # Act
        self.resource.start() # Restart
        
        # Assert
        self.assertEqual(self.resource.get_status(), "Started")
        self.mock_logger.update.assert_called_with("test-app", "Started", unittest.mock.ANY)

    def test_deleted_resource_is_inactive(self):
        """Test that a 'Deleted' resource cannot be started, stopped, or deleted again."""
        # Get the resource into a Deleted state
        self.resource.delete()
        self.assertEqual(self.resource.get_status(), "Deleted")
        self.mock_logger.reset_mock()
        
        # 1. Try to Start
        self.resource.start()
        self.assertEqual(self.resource.get_status(), "Deleted") # State unchanged
        self.mock_logger.update.assert_called_with("test-app", "Error", "Cannot start. Resource has been deleted.")
        self.mock_logger.reset_mock()

        # 2. Try to Stop
        self.resource.stop()
        self.assertEqual(self.resource.get_status(), "Deleted") # State unchanged
        self.mock_logger.update.assert_called_with("test-app", "Error", "Cannot stop. Resource has been deleted.")
        self.mock_logger.reset_mock()

        # 3. Try to Delete again
        self.resource.delete()
        self.assertEqual(self.resource.get_status(), "Deleted") # State unchanged
        self.mock_logger.update.assert_called_with("test-app", "Error", "Resource is already deleted.")
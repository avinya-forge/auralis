import unittest
from typing import Any, Dict, List

from src.services.cloud.provider_interface import CloudProviderInterface


class DummyProvider(CloudProviderInterface):
    """A minimal concrete implementation for testing the interface."""

    @property
    def name(self) -> str:
        return "DummyProvider"

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        return True

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        return True

    def download_file(self, remote_path: str, local_path: str) -> bool:
        return True

    def list_files(self, remote_prefix: str = "") -> List[Dict[str, Any]]:
        return []

    def delete_file(self, remote_path: str) -> bool:
        return True

    def get_quota(self) -> Dict[str, Any]:
        return {"used": 0, "total": 100}


class TestCloudProviderInterface(unittest.TestCase):
    def test_cannot_instantiate_abstract_class(self) -> None:
        """Test that CloudProviderInterface cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            CloudProviderInterface()  # type: ignore

    def test_concrete_class_instantiation(self) -> None:
        """Test that a subclass implementing all methods can be instantiated."""
        provider = DummyProvider()
        self.assertEqual(provider.name, "DummyProvider")

    def test_concrete_methods(self) -> None:
        """Test calling the implemented methods of the dummy subclass."""
        provider = DummyProvider()

        self.assertTrue(provider.authenticate({"key": "val"}))
        self.assertTrue(provider.upload_file("local.txt", "remote.txt"))
        self.assertTrue(provider.download_file("remote.txt", "local.txt"))
        self.assertEqual(provider.list_files(), [])
        self.assertTrue(provider.delete_file("remote.txt"))
        self.assertEqual(provider.get_quota(), {"used": 0, "total": 100})

    def test_incomplete_subclass_fails(self) -> None:
        """Test that a subclass missing a method raises TypeError on instantiation."""

        class IncompleteProvider(CloudProviderInterface):
            @property
            def name(self) -> str:
                return "Incomplete"

            # Missing authenticate, upload, etc.

        with self.assertRaises(TypeError):
            IncompleteProvider()  # type: ignore


if __name__ == "__main__":
    unittest.main()

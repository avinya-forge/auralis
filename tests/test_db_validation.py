import os
import tempfile
import unittest

from src.services.gamification import GamificationService


class TestDBValidation(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.service = GamificationService(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_points_addition(self):
        user_id = "user1"
        stats = self.service.add_validation_points(user_id)

        self.assertEqual(stats["points"], 10)
        self.assertEqual(stats["level"], 1)

        # Verify persistence
        new_stats = self.service.get_user_stats(user_id)
        self.assertEqual(new_stats["points"], 10)
        self.assertEqual(new_stats["validations"], 1)

    def test_level_up(self):
        user_id = "user2"
        # 10 validations = 100 points -> Level 2
        for _ in range(10):
            stats = self.service.add_validation_points(user_id)

        self.assertEqual(stats["points"], 100)
        self.assertEqual(stats["level"], 2)

    def test_get_non_existent_user(self):
        stats = self.service.get_user_stats("ghost")
        self.assertEqual(stats["points"], 0)
        self.assertEqual(stats["level"], 1)


if __name__ == "__main__":
    unittest.main()

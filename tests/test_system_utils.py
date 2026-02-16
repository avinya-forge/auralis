"""
Auralis - System Utilities Test Module
"""

import unittest
from unittest.mock import MagicMock, patch

from src.utils.system_utils import SystemMonitor


class TestSystemUtils(unittest.TestCase):
    """Test system utility functions"""

    def setUp(self):
        """Set up test environment"""
        self.monitor = SystemMonitor()

    @patch("src.utils.system_utils.psutil")
    def test_update_resource_data(self, mock_psutil):
        """Test updating resource data"""
        # Mock psutil calls
        mock_psutil.cpu_percent.return_value = 50.0

        mock_memory = MagicMock()
        mock_memory.percent = 60.0
        mock_memory.available = 8 * 1024 * 1024 * 1024  # 8 GB
        mock_psutil.virtual_memory.return_value = mock_memory

        mock_net = MagicMock()
        mock_net.bytes_sent = 100 * 1024 * 1024
        mock_net.bytes_recv = 200 * 1024 * 1024
        mock_psutil.net_io_counters.return_value = mock_net

        self.monitor._update_resource_data()

        data = self.monitor.resource_data
        self.assertEqual(data["cpu_percent"], 50.0)
        self.assertEqual(data["memory_percent"], 60.0)
        self.assertEqual(data["memory_available"], 8 * 1024)  # 8192 MB
        self.assertEqual(data["network_usage"], 300)  # 300 MB

    @patch("src.utils.system_utils.psutil")
    def test_calculate_optimal_threads(self, mock_psutil):
        """Test calculating optimal threads"""
        # Mock CPU count
        mock_psutil.cpu_count.return_value = 8

        # Scenario 1: Low usage
        self.monitor.resource_data["cpu_percent"] = 20.0
        self.monitor.resource_data["memory_percent"] = 30.0

        self.monitor._calculate_optimal_threads()
        # Should be max(1, 8-1) = 7
        self.assertEqual(self.monitor.resource_data["optimal_threads"], 7)

        # Scenario 2: High CPU usage
        self.monitor.resource_data["cpu_percent"] = 95.0
        self.monitor.resource_data["memory_percent"] = 30.0

        self.monitor._calculate_optimal_threads()
        # Should be max(1, 7 // 2) = 3
        self.assertEqual(self.monitor.resource_data["optimal_threads"], 3)

        # Scenario 3: High Memory usage
        self.monitor.resource_data["cpu_percent"] = 20.0
        self.monitor.resource_data["memory_percent"] = 95.0

        self.monitor._calculate_optimal_threads()
        # Should be max(1, 7 // 2) = 3
        self.assertEqual(self.monitor.resource_data["optimal_threads"], 3)

    @patch("src.utils.system_utils.os")
    @patch("src.utils.system_utils.platform")
    def test_optimize_system(self, mock_platform, mock_os):
        """Test system optimization"""
        mock_platform.system.return_value = "Windows"
        mock_os.environ.get.return_value = "/tmp/temp"
        mock_os.path.exists.return_value = True
        mock_os.listdir.return_value = ["old_file", "new_file", "directory"]

        def mock_join(path, *paths):
            return f"{path}/{paths[0]}"

        mock_os.path.join.side_effect = mock_join

        mock_os.path.isfile.side_effect = lambda p: "directory" not in p

        # Mock time to control file age
        with patch("src.utils.system_utils.time") as mock_time:
            current_time = 1000000
            mock_time.time.return_value = current_time

            # old_file: older than 7 days (7 * 86400 = 604800)
            # new_file: strictly newer
            mock_os.path.getmtime.side_effect = lambda p: (
                current_time - 700000 if "old_file" in p else current_time - 100
            )

            result = self.monitor.optimize_system()

            self.assertTrue(result)
            # old_file should be removed
            mock_os.remove.assert_any_call("/tmp/temp/old_file")
            # new_file should NOT be removed (assert check logic)
            # Since remove is mocked, we need to check call args
            removed_files = [call[0][0] for call in mock_os.remove.call_args_list]
            self.assertIn("/tmp/temp/old_file", removed_files)
            self.assertNotIn("/tmp/temp/new_file", removed_files)

    @patch("src.utils.system_utils.psutil")
    def test_identify_resource_intensive_processes(self, mock_psutil):
        """Test identifying resource intensive processes"""
        # Mock processes
        mock_procs = []
        for i in range(10):
            p = MagicMock()
            p.info = {
                "pid": i,
                "name": f"proc{i}",
                "cpu_percent": i * 5,  # 0, 5, 10, 15... 45
                "memory_percent": 10,
            }
            mock_procs.append(p)

        mock_psutil.process_iter.return_value = mock_procs

        result = self.monitor._identify_resource_intensive_processes()

        # Should return top 5 sorted by CPU desc
        # CPU usage: 45, 40, 35, 30, 25, 20, 15, 10, 5, 0
        # Should filter > 10%
        # So we expect processes with CPU 45, 40, 35, 30, 25, 20, 15
        # But limited to top 5

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["cpu_percent"], 45)
        self.assertEqual(result[4]["cpu_percent"], 25)


if __name__ == "__main__":
    unittest.main()

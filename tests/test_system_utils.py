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

    @patch("src.utils.system_utils.Path")
    @patch("src.utils.system_utils.platform")
    @patch("src.utils.system_utils.os")
    def test_optimize_system(self, mock_os, mock_platform, mock_path):
        """Test system optimization"""
        mock_platform.system.return_value = "Windows"
        mock_os.environ.get.return_value = "/tmp/temp"

        # Mock Path objects
        # We need to handle Path("/tmp/temp") and Path.home() / ...

        # Create a mock for the temp directory path
        mock_temp_dir = MagicMock()
        mock_temp_dir.exists.return_value = True

        # Create a mock for the cache directory path
        mock_cache_dir = MagicMock()
        mock_cache_dir.exists.return_value = True

        # Configure Path constructor to return mock_temp_dir when called with temp path
        # and mock_cache_dir when constructed via home() / ...
        # But Path is called with a string.
        # And Path.home() is a class method.

        def side_effect(arg=None):
            if arg == "/tmp/temp":
                return mock_temp_dir
            if arg is mock_cache_dir:
                return mock_cache_dir
            return MagicMock()  # Return a generic mock for other paths

        mock_path.side_effect = side_effect

        # Setup Path.home()
        mock_home = MagicMock()
        mock_path.home.return_value = mock_home
        # cache_dir = Path.home() / ".auralis" / "cache"
        mock_home.__truediv__.return_value.__truediv__.return_value = mock_cache_dir

        # Mock files in temp dir
        file1 = MagicMock()
        file1.is_file.return_value = True

        file2 = MagicMock()
        file2.is_file.return_value = True

        mock_temp_dir.iterdir.return_value = [file1, file2]

        # Mock files in cache dir (empty for simplicity or add one)
        cache_file = MagicMock()
        cache_file.is_file.return_value = True
        mock_cache_dir.iterdir.return_value = [cache_file]

        # Mock time to control file age
        with patch("src.utils.system_utils.time") as mock_time:
            current_time = 1000000
            mock_time.time.return_value = current_time

            # old_file: older than 7 days (7 * 86400 = 604800)
            file1.stat.return_value.st_mtime = current_time - 700000

            # new_file: strictly newer
            file2.stat.return_value.st_mtime = current_time - 100

            # cache file: doesn't matter age, as age_seconds=0
            cache_file.stat.return_value.st_mtime = current_time - 500

            result = self.monitor.optimize_system()

            self.assertTrue(result)

            # Verify file1 (old temp file) was unlinked
            file1.unlink.assert_called_once()

            # Verify file2 (new temp file) was NOT unlinked
            file2.unlink.assert_not_called()

            # Verify cache_file was unlinked (age_seconds=0 means delete all)
            cache_file.unlink.assert_called_once()

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

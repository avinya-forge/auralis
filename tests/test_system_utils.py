"""
Auralis - System Utilities Test Module
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock psutil if not available
if "psutil" not in sys.modules:
    sys.modules["psutil"] = MagicMock()

from src.utils.system_utils import SystemCleaner, SystemMonitor


class TestSystemCleaner(unittest.TestCase):
    """Test system cleaner functions"""

    @patch("src.utils.system_utils.Path")
    @patch("src.utils.system_utils.platform")
    @patch("src.utils.system_utils.os")
    def test_optimize_system(self, mock_os, mock_platform, mock_path):
        """Test system optimization"""
        mock_platform.system.return_value = "Windows"
        mock_os.environ.get.return_value = "/tmp/temp"

        # Mock Path objects
        mock_temp_dir = MagicMock()
        mock_temp_dir.exists.return_value = True

        mock_cache_dir = MagicMock()
        mock_cache_dir.exists.return_value = True

        def side_effect(arg=None):
            if arg == "/tmp/temp":
                return mock_temp_dir
            if arg is mock_cache_dir:
                return mock_cache_dir
            return MagicMock()

        mock_path.side_effect = side_effect

        mock_home = MagicMock()
        mock_path.home.return_value = mock_home
        mock_home.__truediv__.return_value.__truediv__.return_value = mock_cache_dir

        # Mock files in temp dir
        file1 = MagicMock()
        file1.is_file.return_value = True
        file2 = MagicMock()
        file2.is_file.return_value = True
        mock_temp_dir.iterdir.return_value = [file1, file2]

        # Mock files in cache dir
        cache_file = MagicMock()
        cache_file.is_file.return_value = True
        mock_cache_dir.iterdir.return_value = [cache_file]

        with patch("src.utils.system_utils.time") as mock_time:
            current_time = 1000000
            mock_time.time.return_value = current_time

            # old_file: older than 7 days
            file1.stat.return_value.st_mtime = current_time - 700000
            # new_file: strictly newer
            file2.stat.return_value.st_mtime = current_time - 100
            # cache file: doesn't matter age
            cache_file.stat.return_value.st_mtime = current_time - 500

            result = SystemCleaner.optimize_system()

            self.assertTrue(result)
            file1.unlink.assert_called_once()
            file2.unlink.assert_not_called()
            cache_file.unlink.assert_called_once()


class TestSystemUtils(unittest.TestCase):
    """Test system utility functions"""

    def setUp(self):
        """Set up test environment"""
        self.monitor = SystemMonitor()

    @patch("src.utils.system_utils.psutil")
    def test_update_resource_data(self, mock_psutil):
        """Test updating resource data"""
        mock_psutil.cpu_percent.return_value = 50.0

        mock_memory = MagicMock()
        mock_memory.percent = 60.0
        mock_memory.available = 8 * 1024 * 1024 * 1024
        mock_psutil.virtual_memory.return_value = mock_memory

        mock_net = MagicMock()
        mock_net.bytes_sent = 100 * 1024 * 1024
        mock_net.bytes_recv = 200 * 1024 * 1024
        mock_psutil.net_io_counters.return_value = mock_net

        self.monitor._update_resource_data()

        data = self.monitor.resource_data
        self.assertEqual(data["cpu_percent"], 50.0)
        self.assertEqual(data["memory_percent"], 60.0)
        self.assertEqual(data["memory_available"], 8 * 1024)
        self.assertEqual(data["network_usage"], 300)

    @patch("src.utils.system_utils.psutil")
    def test_calculate_optimal_threads(self, mock_psutil):
        """Test calculating optimal threads"""
        mock_psutil.cpu_count.return_value = 8

        self.monitor.resource_data["cpu_percent"] = 20.0
        self.monitor.resource_data["memory_percent"] = 30.0
        self.monitor._calculate_optimal_threads()
        self.assertEqual(self.monitor.resource_data["optimal_threads"], 7)

        self.monitor.resource_data["cpu_percent"] = 95.0
        self.monitor.resource_data["memory_percent"] = 30.0
        self.monitor._calculate_optimal_threads()
        self.assertEqual(self.monitor.resource_data["optimal_threads"], 3)

        self.monitor.resource_data["cpu_percent"] = 20.0
        self.monitor.resource_data["memory_percent"] = 95.0
        self.monitor._calculate_optimal_threads()
        self.assertEqual(self.monitor.resource_data["optimal_threads"], 3)

    @patch("src.utils.system_utils.SystemCleaner")
    def test_optimize_system_proxy(self, mock_cleaner):
        """Test system optimization proxy"""
        mock_cleaner.optimize_system.return_value = True

        result = self.monitor.optimize_system()

        self.assertTrue(result)
        mock_cleaner.optimize_system.assert_called_once()

    @patch("src.utils.system_utils.psutil")
    def test_identify_resource_intensive_processes(self, mock_psutil):
        """Test identifying resource intensive processes"""
        mock_procs = []
        for i in range(10):
            p = MagicMock()
            p.info = {
                "pid": i,
                "name": f"proc{i}",
                "cpu_percent": i * 5,
                "memory_percent": 10,
            }
            mock_procs.append(p)

        mock_psutil.process_iter.return_value = mock_procs

        result = self.monitor._identify_resource_intensive_processes()

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["cpu_percent"], 45)
        self.assertEqual(result[4]["cpu_percent"], 25)


if __name__ == "__main__":
    unittest.main()

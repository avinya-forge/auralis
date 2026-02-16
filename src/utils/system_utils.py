"""
Auralis - System Utilities Module

Monitors and manages system resources for optimal performance
"""

import os
import platform
import threading
import time
from pathlib import Path

import psutil  # type: ignore
from PyQt6.QtCore import QObject, pyqtSignal


class SystemMonitor(QObject):
    """
    Monitors system resources and provides optimal thread counts
    """

    resources_updated = pyqtSignal(dict)  # system resource info

    def __init__(self, update_interval=5):
        """
        Initialize the system monitor

        Args:
            update_interval (int): Update interval in seconds
        """
        super().__init__()
        self.update_interval = update_interval
        self.running = False
        self.monitor_thread = None
        self.resource_data = {
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_available": 0,
            "network_usage": 0,
            "optimal_threads": 1,
        }

    def start_monitoring(self):
        """Start monitoring system resources"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring system resources"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def _monitor_loop(self):
        """Monitor loop that runs in a separate thread"""
        # Initial delay to let system stabilize
        time.sleep(1)

        while self.running:
            try:
                self._update_resource_data()
                self._calculate_optimal_threads()
                self.resources_updated.emit(self.resource_data)
                time.sleep(self.update_interval)

            except Exception as e:
                print(f"Error monitoring system resources: {str(e)}")
                time.sleep(self.update_interval)

    def _update_resource_data(self):
        """Update system resource data"""
        self.resource_data["cpu_percent"] = psutil.cpu_percent(interval=1)

        memory = psutil.virtual_memory()
        self.resource_data["memory_percent"] = memory.percent
        self.resource_data["memory_available"] = memory.available / (1024 * 1024)  # MB

        net_io = psutil.net_io_counters()
        self.resource_data["network_usage"] = (net_io.bytes_sent + net_io.bytes_recv) / (
            1024 * 1024
        )  # MB

    def _adjust_threads_cpu(self, optimal):
        """Adjust thread count based on CPU usage"""
        if self.resource_data["cpu_percent"] > 90:
            return max(1, optimal // 2)
        elif self.resource_data["cpu_percent"] > 80:
            return max(1, optimal - 2)
        elif self.resource_data["cpu_percent"] > 60:
            return max(1, optimal - 1)
        return optimal

    def _adjust_threads_memory(self, optimal):
        """Adjust thread count based on memory usage"""
        if self.resource_data["memory_percent"] > 90:
            return max(1, optimal // 2)
        elif self.resource_data["memory_percent"] > 85:
            return max(1, optimal - 2)
        elif self.resource_data["memory_percent"] > 70:
            return max(1, optimal - 1)
        return optimal

    def _calculate_optimal_threads(self):
        """Calculate optimal thread count based on system resources"""
        cpu_count = psutil.cpu_count(logical=True)
        optimal = max(1, cpu_count - 1)  # Leave one CPU for system

        optimal = self._adjust_threads_cpu(optimal)
        optimal = self._adjust_threads_memory(optimal)

        self.resource_data["optimal_threads"] = optimal

    def get_optimal_thread_count(self):
        """
        Get the optimal thread count for processing

        Returns:
            int: Optimal thread count
        """
        return self.resource_data["optimal_threads"]

    def _clean_temp_files(self):
        """Clean user temporary files older than 7 days"""
        if platform.system() != "Windows":
            return

        temp_dir = os.environ.get("TEMP")
        if not temp_dir or not os.path.exists(temp_dir):
            return

        now = time.time()
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isfile(item_path):
                try:
                    if os.path.getmtime(item_path) < (now - 7 * 86400):
                        os.remove(item_path)
                except (PermissionError, OSError):
                    pass

    def _clean_app_cache(self):
        """Clean application cache"""
        cache_dir = os.path.join(str(Path.home()), ".auralis", "cache")
        if not os.path.exists(cache_dir):
            return

        for item in os.listdir(cache_dir):
            item_path = os.path.join(cache_dir, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
            except (PermissionError, OSError):
                pass

    def optimize_system(self):
        """
        Optimize system by cleaning up temporary files and cache

        Returns:
            bool: True if optimization was successful
        """
        try:
            self._clean_temp_files()
            self._clean_app_cache()
            return True
        except Exception as e:
            print(f"Error optimizing system: {str(e)}")
            return False

    def _collect_processes(self):
        """Collect running processes with resource info"""
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    def _identify_resource_intensive_processes(self):
        """
        Identify resource-intensive processes that might affect performance

        Returns:
            list: List of resource-intensive processes
        """
        try:
            processes = self._collect_processes()

            # Sort by CPU usage
            processes = sorted(processes, key=lambda p: p.get("cpu_percent", 0), reverse=True)

            intensive_processes = []
            # Return top 5 processes using significant CPU
            for proc in processes[:5]:
                if proc.get("cpu_percent", 0) > 10:  # Only include if using >10% CPU
                    intensive_processes.append(
                        {
                            "pid": proc.get("pid"),
                            "name": proc.get("name"),
                            "cpu_percent": proc.get("cpu_percent", 0),
                            "memory_percent": proc.get("memory_percent", 0),
                        }
                    )
            return intensive_processes

        except Exception as e:
            print(f"Error identifying resource-intensive processes: {str(e)}")
            return []

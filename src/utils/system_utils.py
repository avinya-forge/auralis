"""
Auralis - System Utilities Module

Monitors and manages system resources for optimal performance
"""

import os
import psutil
import threading
import time
import platform
from PyQt6.QtCore import QObject, pyqtSignal
from pathlib import Path


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
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_available': 0,
            'network_usage': 0,
            'optimal_threads': 1
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
                # Update resource data
                self._update_resource_data()

                # Calculate optimal thread count
                self._calculate_optimal_threads()

                # Emit signal with updated data
                self.resources_updated.emit(self.resource_data)

                # Sleep for the update interval
                time.sleep(self.update_interval)

            except Exception as e:
                print(f"Error monitoring system resources: {str(e)}")
                time.sleep(self.update_interval)

    def _update_resource_data(self):
        """Update system resource data"""
        # CPU usage
        self.resource_data['cpu_percent'] = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        self.resource_data['memory_percent'] = memory.percent
        self.resource_data['memory_available'] = memory.available / (1024 * 1024)  # MB

        # Network usage (simplified)
        net_io = psutil.net_io_counters()
        self.resource_data['network_usage'] = (
            net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB

    def _calculate_optimal_threads(self):
        """Calculate optimal thread count based on system resources"""
        # Start with logical CPU count
        cpu_count = psutil.cpu_count(logical=True)

        # Base optimal threads on CPU count
        optimal = max(1, cpu_count - 1)  # Leave one CPU for system

        # Adjust based on current CPU usage - more aggressive scaling
        if self.resource_data['cpu_percent'] > 90:
            optimal = max(1, optimal // 2)  # Cut in half if very high CPU
        elif self.resource_data['cpu_percent'] > 80:
            optimal = max(1, optimal - 2)
        elif self.resource_data['cpu_percent'] > 60:
            optimal = max(1, optimal - 1)

        # Adjust based on memory usage - more aggressive scaling
        if self.resource_data['memory_percent'] > 90:
            optimal = max(1, optimal // 2)  # Cut in half if very high memory
        elif self.resource_data['memory_percent'] > 85:
            optimal = max(1, optimal - 2)
        elif self.resource_data['memory_percent'] > 70:
            optimal = max(1, optimal - 1)

        # Final adjustment
        self.resource_data['optimal_threads'] = optimal

    def get_optimal_thread_count(self):
        """
        Get the optimal thread count for processing

        Returns:
            int: Optimal thread count
        """
        return self.resource_data['optimal_threads']

    def optimize_system(self):
        """
        Optimize system by cleaning up temporary files and cache

        Returns:
            bool: True if optimization was successful
        """
        try:
            if platform.system() == 'Windows':
                # Clean only user temp files, not all system temp files
                temp_dir = os.environ.get('TEMP')
                if temp_dir and os.path.exists(temp_dir):
                    # Use a safer, more targeted approach
                    # Delete only files older than 7 days
                    now = time.time()
                    for item in os.listdir(temp_dir):
                        item_path = os.path.join(temp_dir, item)
                        # Only delete files, not directories
                        if os.path.isfile(item_path):
                            try:
                                # Check if file is older than 7 days
                                if os.path.getmtime(item_path) < (now - 7 * 86400):
                                    os.remove(item_path)
                            except (PermissionError, OSError):
                                # Skip files that can't be accessed
                                pass

            # Clear application cache if it exists
            cache_dir = os.path.join(str(Path.home()), '.auralis', 'cache')
            if os.path.exists(cache_dir):
                for item in os.listdir(cache_dir):
                    item_path = os.path.join(cache_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                    except (PermissionError, OSError):
                        pass

            return True

        except Exception as e:
            print(f"Error optimizing system: {str(e)}")
            return False

    def _identify_resource_intensive_processes(self):
        """
        Identify resource-intensive processes that might affect performance

        Returns:
            list: List of resource-intensive processes
        """
        intensive_processes = []

        try:
            # Get all processes sorted by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # Sort by CPU usage
            processes = sorted(processes, key=lambda p: p.get('cpu_percent', 0), reverse=True)

            # Return top 5 processes using significant CPU
            for proc in processes[:5]:
                if proc.get('cpu_percent', 0) > 10:  # Only include if using >10% CPU
                    intensive_processes.append({
                        'pid': proc.get('pid'),
                        'name': proc.get('name'),
                        'cpu_percent': proc.get('cpu_percent', 0),
                        'memory_percent': proc.get('memory_percent', 0)
                    })

        except Exception as e:
            print(f"Error identifying resource-intensive processes: {str(e)}")

        return intensive_processes

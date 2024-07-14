# self_healing.py (c) 2024 Gregory L. Magnusson MIT license
# AGI awareness as self correction
import logging
import time
import traceback
import psutil
import subprocess
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

class SelfHealingSystem:
    """
    Self-Healing System class that monitors and heals itself.
    """

    def __init__(self, check_interval=10):
        """
        Initializes the self-healing system.
        
        :param check_interval: Time interval (in seconds) between health checks
        """
        self.check_interval = check_interval

    def is_system_healthy(self) -> bool:
        """
        Checks if the system is healthy.
        
        :returns: True if the system is healthy, False otherwise.
        """
        try:
            logging.info("Checking system health...")
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_usage = psutil.disk_usage('/')
            health_status = cpu_usage < 80 and memory_info.percent < 80 and disk_usage.percent < 80
            logging.info(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_info.percent}%, Disk Usage: {disk_usage.percent}%")
            return health_status
        except Exception as e:
            logging.error(f"Error checking system health: {e}")
            return False

    def heal_system(self):
        """
        Tries to heal the system if an issue is detected.
        """
        try:
            logging.info("Attempting to heal the system...")
            # Example heal method: Restarting a service (placeholder)
            self.restart_service("example_service")
        except Exception as e:
            logging.error(f"Error during healing process: {e}")
            logging.debug(traceback.format_exc())
    
    def monitor(self):
        """
        Continuously monitors the system and applies healing mechanisms if needed.
        """
        while True:
            if self.is_system_healthy():
                logging.info("System is healthy.")
            else:
                logging.error("System is unhealthy! Initiating heal process.")
                self.heal_system()
            time.sleep(self.check_interval)

    def check_database_connection(self) -> bool:
        """
        Check if the database connection is alive.

        :returns: True if connection is alive, otherwise False.
        """
        try:
            # Placeholder for actual database connection check.
            # db_connection = self.get_database_connection()
            # return db_connection.is_alive()
            return True  # Simulating a live database connection.
        except Exception as e:
            logging.error(f"Database connection check failed: {e}")
            return False
        
    def restart_service(self, service_name: str):
        """
        Restart the given service.

        :param service_name: Name of the service to restart.
        """
        try:
            logging.info(f"Restarting service: {service_name}")
            # Placeholder for actual service restart logic.
            subprocess.run(['sudo', 'systemctl', 'restart', service_name], check=True)
            logging.info(f"Service {service_name} restarted successfully.")
        except Exception as e:
            logging.error(f"Failed to restart service {service_name}: {e}")

    def check_disk_space(self) -> bool:
        """
        Check if there is enough disk space available.

        :returns: True if disk space is sufficient, otherwise False.
        """
        try:
            disk_usage = psutil.disk_usage('/')
            if disk_usage.percent > 90:
                logging.warning(f"Disk space critically low: {disk_usage.percent}% used.")
                return False
            return True
        except Exception as e:
            logging.error(f"Error checking disk space: {e}")
            return False

    def free_up_disk_space(self):
        """
        Free up disk space by removing unnecessary files or logs.
        """
        try:
            logging.info("Freeing up disk space...")
            # Placeholder for disk cleanup logic.
            logs_dir = "/var/log"
            for root, dirs, files in os.walk(logs_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.getsize(file_path) > 10 * 1024 * 1024:  # If file is larger than 10MB
                        os.remove(file_path)
                        logging.info(f"Removed large log file: {file_path}")
        except Exception as e:
            logging.error(f"Failed to free up disk space: {e}")

    def restart_system(self):
        """
        Restart the entire system.
        """
        try:
            logging.info("Restarting the system...")
            subprocess.run(['sudo', 'reboot'], check=True)
        except Exception as e:
            logging.error(f"Failed to restart the system: {e}")

    def retrain_model(self, epochs=100):
        """
        Retrain a model with new data.
        
        :param epochs: Number of epochs to train the model.
        """
        try:
            logging.info(f"Retraining model for {epochs} epochs...")
            # Placeholder for actual retraining logic.
            # model.train(new_data, epochs=epochs)
        except Exception as e:
            logging.error(f"Error retraining model: {e}")
            logging.debug(traceback.format_exc())

# Example usage
if __name__ == "__main__":
    healer = SelfHealingSystem(check_interval=5)
    healer.monitor()


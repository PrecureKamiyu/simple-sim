"""
Device Manager class.
"""
from __future__ import annotations
from typing import List
import logging
from network_manager import NetworkManager  # Import NetworkManager from network_manager module
from task import Task
from device import DeviceStatus

logging.basicConfig(filename='device_manager.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EdgeDeviceManager:
    def __init__(self, device_context):
        self.context = device_context
        self.context.init()
        self.working_devices_count: int = 0

    def is_done(self) -> bool:
        # Check if all tasks are completed
        return all(device.device_status == DeviceStatus.DONE for device in self.context.vm_list)

    def run(self):
        for device in self.context.vm_list:
            device.run()
        logging.info("Edge devices ran tasks.")

    def assign_tasks(self, tasks: List[Task]):
        num_devices = len(self.context.vm_list)
        for i, task in enumerate(tasks):
            device_index = i % num_devices
            device = self.context.vm_list[device_index]
            device.add_task(task)
            logging.info(f"Assigned task {task} to device {device.device_id}.")

    def communicate(self, network_manager: NetworkManager):
        for device in self.context.vm_list:
            frequency = network_manager.get_frequency(device.device_id)
            if frequency:
                logging.info(f"Device {device.device_id} is communicating on frequency {frequency}")
            else:
                logging.info(f"Device {device.device_id} does not have a frequency assigned")


class ServerManager:
    def __init__(self, device_context):
        self.context = device_context
        self.context.init()
        self.working_servers_count: int = 0

    def is_done(self) -> bool:
        # Check if all tasks are completed
        return all(server.device_status == DeviceStatus.DONE for server in self.context.server_list)

    def run(self):
        for server in self.context.server_list:
            server.run()
        logging.info("Servers ran tasks.")

    def assign_tasks(self, tasks: List[Task]):
        num_servers = len(self.context.server_list)
        for i, task in enumerate(tasks):
            server_index = i % num_servers
            server = self.context.server_list[server_index]
            server.add_task(task)
            logging.info(f"Assigned task {task} to server {server.server_id}.")

    def communicate(self, network_manager: NetworkManager):
        for server in self.context.server_list:
            frequency = network_manager.get_frequency(server.server_id)
            if frequency:
                logging.info(f"Server {server.server_id} is communicating on frequency {frequency}")
            else:
                logging.info(f"Server {server.server_id} does not have a frequency assigned")

"""
Server Manager class.
"""
from __future__ import annotations
from enum import Enum
import random
from typing import Optional, List
from typing import List
import logging
from queue import Queue
from context import EdgeDeviceManagerContext, ServerManagerContext  # Import EdgeDeviceManagerContext and ServerManagerContext from context module
from network_manager import NetworkManager  # Import NetworkManager from network_manager module
from task import Task, TaskType, TaskStatus  # Import Task, TaskType, and TaskStatus from task module

logging.basicConfig(filename='server_manager.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DeviceStatus(Enum):
    DONE = "DONE"


class EdgeDeviceManager:
    def __init__(self, device_context):
        self.context = device_context
        self.context.init()
        self.working_devices_count: int = 0

    def is_done(self) -> bool:
        done = all(getattr(element, 'device_status') == DeviceStatus.DONE for element in self.context.vm_list)
        if done:
            logging.info("All edge devices are done.")
        return done

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
        done = all(getattr(element, 'device_status') == DeviceStatus.DONE for element in self.context.server_list)
        if done:
            logging.info("All servers are done.")
        return done

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

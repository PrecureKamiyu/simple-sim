"""
Device class.
"""
from __future__ import annotations
import logging
from enum import Enum

logging.basicConfig(filename='device.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DeviceStatus(Enum):
    CREATED = "CREATED"
    DONE = "DONE"


class EdgeDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.device_status = DeviceStatus.CREATED
        self.tasks = []

    def run(self):
        self.device_status = DeviceStatus.DONE
        logging.info(f"Device {self.device_id} ran task.")

    def add_task(self, task):
        self.tasks.append(task)
        logging.info(f"Task {task} added to device {self.device_id}.")


class Server:
    def __init__(self, server_id, x, y, coverage_range):
        self.server_id = server_id
        self.device_status = DeviceStatus.CREATED
        self.tasks = []
        self.x = x
        self.y = y
        self.coverage_range = coverage_range

    def run(self):
        self.device_status = DeviceStatus.DONE
        logging.info(f"Server {self.server_id} ran task.")

    def add_task(self, task):
        self.tasks.append(task)
        logging.info(f"Task {task} added to server {self.server_id}.")

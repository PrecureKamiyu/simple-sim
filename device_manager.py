"""
Device Manager class.
"""
from __future__ import annotations
from enum import Enum
import random
from typing import Optional, List
from typing import List
import logging
from queue import Queue
from context import EdgeDeviceManagerContext, ServerManagerContext  # Import EdgeDeviceManagerContext and ServerManagerContext from context module
from task import Task  # Import Task from task module

logging.basicConfig(filename='device_manager.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DeviceStatus(Enum):
    DONE = "DONE"


class DeviceManager:
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

    def __init__(self, device_context):
        self.context = device_context
        self.context.init()
        self.working_devices_count: int = 0


class EdgeDeviceManager(DeviceManager):
    def __init__(self, edge_device_context: EdgeDeviceManagerContext):
        super().__init__(edge_device_context)


class ServerManager(DeviceManager):
    def __init__(self, server_context: ServerManagerContext):
        super().__init__(server_context)

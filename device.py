"""
Device class.
"""
from __future__ import annotations
from enum import Enum
import random
from typing import Optional, List
import logging
from queue import Queue
from task import Task, TaskStatus  # Import Task and TaskStatus from task module

logging.basicConfig(filename='device.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DeviceStatus(Enum):
    CREATED = "CREATED"
    WORKING = "WORKING"
    DONE    = "DONE"

    def transition(self, new_state):
        if self == DeviceStatus.CREATED and new_state == DeviceStatus.WORKING:
            return True
        elif self == DeviceStatus.WORKING and new_state == DeviceStatus.DONE:
            return True
        else:
            return False


class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.efforts = 0
        self.tasks: Queue = Queue()
        self.current_task: Optional[Task] = None
        self.device_status = DeviceStatus.CREATED

    def is_busy(self) -> bool:
        return self.efforts != 0

    def calculate_efforts(self, process_size) -> int:
        return 10

    def reset_process_time(self):
        pass

    def get_process_time(self) -> float:
        return 10.0

    def add_task(self, task: Task):
        self.tasks.put(task)


class EdgeDevice(Device):
    def __init__(self,
                 edge_device_id: int):
        super().__init__(edge_device_id)

    def run(self):
        if self.is_busy():
            self.efforts -= 1
            logging.info(f"Device {self.device_id} task {self.current_task.task_id} efforts minus one.")
            return

        if self.current_task and self.current_task.status == TaskStatus.PROCESSING:
            logging.info(f"Device {self.device_id} completed task {self.current_task.task_id}.")
            self.current_task = None

        if self.current_task is None and not self.tasks.empty():
            task = self.tasks.get()
            task.status = TaskStatus.PROCESSING
            self.efforts = self.calculate_efforts(task.process_size)
            self.current_task = task
            if self.device_status.transition(DeviceStatus.WORKING):
                self.device_status = DeviceStatus.WORKING
                logging.info(f"Device {self.device_id} started task {task.task_id}.")

        if self.current_task is None and self.tasks.empty():
            if self.device_status.transition(DeviceStatus.DONE):
                self.device_status = DeviceStatus.DONE
                logging.info(f"Device {self.device_id} is done.")


class Server(Device):
    def __init__(self, server_id: int, cpu_speed: float = 0, memory_size: int = 0, storage_size: int = 0, network_bandwidth: float = 0, x: float = 0, y: float = 0, coverage_range: float = 0):
        super().__init__(server_id)
        self.cpu_speed = cpu_speed
        self.memory_size = memory_size
        self.storage_size = storage_size
        self.network_bandwidth = network_bandwidth
        self.load = 0
        self.cpu_utilization = 0.0
        self.x = x
        self.y = y
        self.coverage_range = coverage_range
        self.task_queue = Queue()

    def assign_load(self, load: int):
        self.load += load
        self.cpu_utilization = self.calculate_cpu_utilization()

    def calculate_cpu_utilization(self) -> float:
        # Placeholder for CPU utilization calculation
        return random.uniform(0.0, 1.0)

    def allocate_resources(self, task: Task):
        # Placeholder for resource allocation logic
        pass

    def add_task(self, task: Task):
        self.task_queue.put(task)

    def run(self):
        if self.is_busy():
            self.efforts -= 1
            logging.info(f"Device {self.device_id} task {self.current_task.task_id} efforts minus one.")
            return

        if self.current_task and self.current_task.status == TaskStatus.PROCESSING:
            logging.info(f"Device {self.device_id} completed task {self.current_task.task_id}.")
            self.current_task = None

        if self.current_task is None and not self.task_queue.empty():
            task = self.task_queue.get()
            task.status = TaskStatus.PROCESSING
            self.efforts = self.calculate_efforts(task.process_size)
            self.current_task = task
            if self.device_status.transition(DeviceStatus.WORKING):
                self.device_status = DeviceStatus.WORKING
                logging.info(f"Device {self.device_id} started task {task.task_id}.")

        if self.current_task is None and self.task_queue.empty():
            if self.device_status.transition(DeviceStatus.DONE):
                self.device_status = DeviceStatus.DONE
                logging.info(f"Device {self.device_id} is done.")

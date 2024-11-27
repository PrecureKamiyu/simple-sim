"""Import Protocol for OOP."""
from __future__ import annotations
import logging
from device_manager import EdgeDeviceManager, ServerManager  # Import EdgeDeviceManager and ServerManager from device_manager module
from task import TaskManager  # Import TaskManager from task module

logging.basicConfig(filename='simulator.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


global_device_id_counter = 0

class Scheduler:
    """
    Scheduler gets tasks and send tasks to managers.
    """

    def __init__(self,
                 orchestrator: Orchestrator):
        self.orchestrator = orchestrator

    def start(self):
        logging.info("Scheduler started.")
        while not self.orchestrator.is_done():
            self.orchestrator.assign_tasks()
            self.orchestrator.offload()
            self.orchestrator.orient()
            self.orchestrator.run()
        logging.info("Scheduler completed.")


class Orchestrator:
    """
    Orchestrator. The name might not be very precise.
    In this case is responsible for offloading decision.
    There are four function for orchestrator.

    1. assign tasks
    2. offload
    3. run
    4. orient

    Run is sending signals for devices and servers to run the
    tasks. Orient is for managing the transfering of the tasks.
    Uploading and downloading is considered as the same thing,
    i.e., transfering tasks, which is managed by TaskManager.
    """

    def __init__(self,
                 edge_device_manager: EdgeDeviceManager,
                 server_manager: ServerManager,
                 task_manager: TaskManager):

        self.edge_device_manager: EdgeDeviceManager = edge_device_manager
        self.server_manager = server_manager
        self.task_manager = task_manager

    def assign_tasks(self):
        if self.task_manager.is_done():
            return
        tasks = self.task_manager.generate_tasks()
        self.edge_device_manager.assign_tasks(tasks)
        logging.info(f"Assigned {len(tasks)} tasks to edge devices.")

    def offload(self):
        # no offloading for now
        logging.info("Offloading tasks (placeholder).")
        pass

    def run(self):
        # this is for devices and servers to run the tasks
        # run should let the devices change the status of tasks
        self.edge_device_manager.run()
        self.server_manager.run()
        logging.info("Ran tasks on edge devices and servers.")

    def orient(self):
        # the tasks has destination, orient is used for guide task to its
        # destination.
        logging.info("Orienting tasks (placeholder).")
        pass

    def is_done(self) -> bool:
        done = self.edge_device_manager.is_done() and self.server_manager.is_done() and self.task_manager.is_done()
        if done:
            logging.info("All tasks are completed.")
        return done

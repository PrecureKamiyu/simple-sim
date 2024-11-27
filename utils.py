"""
Import Protocol for OOP.
"""
from __future__ import annotations
import logging
from device_manager import EdgeDeviceManager, ServerManager
from task import TaskManager, Task
from context import EdgeDeviceManagerContext, ServerManagerContext
from simulator import NetworkManager, Orchestrator, Scheduler

logging.basicConfig(filename='utils.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EdgeDeviceConfig():
    def __init__(self):
        self.edge_device_number: int = 10


class ServerConfig():
    def __init__(self):
        self.server_number: int = 10


class Config():

    def __init__(self):
        self.round: int = 1
        self.edge_device_number: int = 10
        self.server_number: int = 10
        self.tasks_number: int = 1000
        self.tasks_size: int = 100


class ConfigurationLoader():

    def __init__(self):
        self.configuration_folder: str = ""


    def load(self) -> Config:
        return Config()


    def example_load(self):
        pass


class Runner():

    def __init__(self):

        self.configuration_loader: ConfigurationLoader = ConfigurationLoader()


    def start(self):

        config: Config = self.configuration_loader.load()
        edge_device_context: EdgeDeviceManagerContext = EdgeDeviceManagerContext(config.edge_device_number)
        server_context: ServerManagerContext = ServerManagerContext(config.server_number)

        edge_device_manager: EdgeDeviceManager = EdgeDeviceManager(edge_device_context)
        server_manager: ServerManager = ServerManager(server_context)
        network_manager: NetworkManager = NetworkManager(edge_device_context, server_context)
        task_manager: TaskManager = TaskManager(network_manager, config.tasks_number, config.tasks_size)

        orchestrator: Orchestrator = Orchestrator(edge_device_manager, server_manager, task_manager)
        scheduler: Scheduler = Scheduler(orchestrator)

        for _ in range(config.round):
            scheduler.start()

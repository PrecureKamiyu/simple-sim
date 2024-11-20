from simulator import EdgeDeviceManagerContext, Orchestrator, Scheduler, ServerManagerContext, EdgeDeviceManager, ServerManager, NetworkManager, TaskManager


class EdgeDeviceConfig():
    pass


class ServerConfig():
    pass


class Config():

    def __init__(self):
        self.round = 1
        self.edge_device_number: int = 10
        self.server_number: int = 10
        self.tasks_number: int = 1000
        self.tasks_size: int = 100
        pass


class ConfigurationLoader():

    def __init__(self):
        self.configuration_folder = ""
        pass

    def load(self) -> Config:
        return Config()

    def example_load(self):
        pass


class Runner():

    def __init__(self):

        self.configuration_loader = ConfigurationLoader()

    def start(self):

        config: Config                                = self.configuration_loader.load()
        edge_device_context: EdgeDeviceManagerContext = EdgeDeviceManagerContext(config.edge_device_number)
        server_context: ServerManagerContext          = ServerManagerContext(config.server_number)

        edge_device_manager: EdgeDeviceManagerContext = EdgeDeviceManager(edge_device_context)
        server_manager: ServerManager                 = ServerManager(server_context)
        network_manager: NetworkManager               = NetworkManager(edge_device_context, server_context)
        task_manager: TaskManager                     = TaskManager(network_manager, config.tasks_number, config.tasks_size)

        orchestrator: Orchestrator                    = Orchestrator(edge_device_manager, server_manager, task_manager)
        scheduler: Scheduler                          = Scheduler(orchestrator)

        for _ in range(config.round):
            scheduler.start()

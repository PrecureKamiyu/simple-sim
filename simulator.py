"""Import Protocol for OOP."""
from __future__ import annotations
from enum import Enum
import random
from typing import Optional
import logging
from queue import Queue

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


class EdgeDeviceManagerContext:

    def __init__(self, total: int):
        self.vm_list: list[EdgeDevice] = []
        self.total = total

    def init(self):
        global global_device_id_counter
        # create vm_list
        for _ in range(self.total):
            self.vm_list.append(EdgeDevice(global_device_id_counter))
            global_device_id_counter += 1


class EdgeDeviceManager:

    def __init__(self,
                 edge_device_context: EdgeDeviceManagerContext):

        self.context: EdgeDeviceManagerContext = edge_device_context
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

    def assign_tasks(self, tasks: list[Task]):
        num_devices = len(self.context.vm_list)
        for i, task in enumerate(tasks):
            device_index = i % num_devices
            device = self.context.vm_list[device_index]
            device.add_task(task)
            logging.info(f"Assigned task {task.task_id} to device {device.device_id}.")

    def run(self):
        for device in self.context.vm_list:
            device.run()
        logging.info("Edge devices ran tasks.")


class ServerManagerContext:

    def __init__(self, total: int):
        self.server_list: list[Server] = []
        self.total = total

    def init(self, server_manager: ServerManager):
        global global_device_id_counter
        # create server list here
        for _ in range(self.total):
            self.server_list.append(Server(global_device_id_counter))
            global_device_id_counter += 1


class ServerManager:

    def __init__(self,
                 server_context: ServerManagerContext):
        self.context = server_context
        self.context.init(self)
        self.working_servers_count: int = 0

    def is_done(self) -> bool:
        done = all(getattr(server, 'device_status') == DeviceStatus.DONE for server in self.context.server_list)
        if done:
            logging.info("All servers are done.")
        return done

    def run(self):
        for server in self.context.server_list:
            server.run()
            if server.device_status == DeviceStatus.DONE:
                logging.info(f"Server {server.device_id} is done.")
        logging.info("Servers ran tasks.")

    def example_distribute_load(self, load):
        for server in self.context.server_list:
            if server.load < 50:
                server.assign_load(load)
                break

    def run(self):
        for server in self.context.server_list:
            server.run()
            if server.device_status == DeviceStatus.DONE:
                logging.info(f"Server {server.device_id} is done.")
        logging.info("Servers ran tasks.")

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


class EdgeDevice(Device):
    def __init__(self,
                 edge_device_id: int):
        super().__init__(edge_device_id)


class Server(Device):
    def __init__(self, server_id: int, cpu_speed: float = 0, memory_size: int = 0, storage_size: int = 0, network_bandwidth: float = 0):
        super().__init__(server_id)
        self.cpu_speed = cpu_speed
        self.memory_size = memory_size
        self.storage_size = storage_size
        self.network_bandwidth = network_bandwidth
        self.load = 0
        self.cpu_utilization = 0.0

    def assign_load(self, load: int):
        self.load += load
        self.cpu_utilization = self.calculate_cpu_utilization()

    def calculate_cpu_utilization(self) -> float:
        # Placeholder for CPU utilization calculation
        return random.uniform(0.0, 1.0)

    def allocate_resources(self, task: Task):
        # Placeholder for resource allocation logic
        pass


from network_topology_manager import NetworkTopologyManager

class NetworkManager:

    def __init__(self,
                 edge_device_context: EdgeDeviceManagerContext,
                 server_context: ServerManagerContext):
        self.edge_device_context = edge_device_context
        self.server_context      = server_context
        self.topology_manager    = NetworkTopologyManager()

    def calculate_delay(self, data_size, bandwidth) -> float:
        return data_size / bandwidth + random.uniform(0, 0.1)

    def update_network(self):
        self.topology_manager.update_topology()

    def get_device_info(self, device_id):
        return self.topology_manager.get_device_info(device_id)


class TaskStatus(Enum):
    CREATED = "CREATED"
    WAIT_TO_UPLOAD = "WAIT_TO_UPLOAD"
    WAIT_TO_SCHEDULE = "WAIT_TO_SCHEDULE"
    WAIT_TO_PROCESS = "WAIT_TO_PROCESS"
    WAIT_TO_DOWNLOAD = "WAIT_TO_DOWNLOAD"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    DOWNLOADING = "DOWNLOADING"
    COMPLETED = "COMPLETED"
    UNFINISHED = "UNFINISHED"
    REJECTED = "REJECTED"


# TASK_TYPE:n
# NORMAL （普通）
# PARALLEL （并行分片）
# PARALLEL_CHILD （并行分片子任务）
# SEQUENCE （顺序分片）
# SEQUENCE_CHILD （顺序分片子任务）
class TaskError(Enum):
    NO_ERROR = "NO_ERROR"
    UNKNOWN = "UNKNOWN"
    TIMEOUT = "TIMEOUT"
    REJECTED_DUE_TO_TIMEOUT = "REJECTED_DUE_TO_TIME"
    REJECTED_DUE_TO_MEMORY = "REJECTED_DUE_TO_MEMORY"
    REJECTED_DUE_TO_CHANNEL = "REJECTED_DUE_TO_CHANNEL"
    REJECTED_DUE_TO_COVERAGE = "REJECTED_DUE_TO_COVERAGE"


class TaskType(Enum):
    NORMAL = "NORMAL"
    PARALLEL = "PARALLEL"
    PARALLEL_CHILD = "PARALLEL_CHILD"
    SEQUENCE = "SEQUENCE"
    SEQUENCE_CHILD = "SEQUENCE_CHILD"


class TargetType(Enum):
    NO_TARGET = "NO_TARGET"
    SERVER = "SERVER"
    EDGE_DEVICE = "EDGE_DEVICE"


class Task:

    def __init__(self,
                 task_id: int,
                 task_context,
                 task_type: TaskType = TaskType.NORMAL,
                 task_status: TaskStatus = TaskStatus.CREATED,
                 src_device: int = 0,
                 dst_device: int = 0,
                 create_time: float = 0,
                 used_time: float = 0,
                 process_size: float = 100):

        self.task_id      = task_id
        self.context      = task_context
        self.type         = task_type
        self.status       = task_status
        self.src_device   = src_device
        self.dst_device   = dst_device
        self.create_time  = create_time
        self.used_time    = used_time
        self.process_size = process_size


class TaskManager:
    """
    Task Manager will commute with network manager for calculating the
    network delay. The delay will be stored in task structrue.
    """

    def __init__(self,
                 network_manager: NetworkManager,
                 task_number: int,
                 task_size: int):

        self.network_manager = network_manager
        self.task_size = task_size
        self.task_number = task_number
        self.current_id = -1
        self.task_count = 0

    def generate_one_task(self) -> Task:
        self.current_id += 1
        return Task(task_id=self.current_id,
                    task_context=None,
                    task_type=TaskType.NORMAL,
                    task_status=TaskStatus.CREATED,
                    process_size=self.task_size)

    def is_done(self) -> bool:
        done = self.task_count >= self.task_number
        if done:
            logging.info("All tasks are generated.")
        return done

    def generate_tasks(self) -> list[Task]:
        """
        A strategy of generating tasks can be implemented here.
        """
        ret = []
        self.task_count += 10
        for _ in range(10):
            ret.append(self.generate_one_task())
        logging.info(f"Generated {len(ret)} tasks.")
        return ret

    def transfer_task(self, src, dst, task):
        """
        Called by offloader and others.
        The delay is calculated using network module.
        And then the delay is recorded.
        """
        pass

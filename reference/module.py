from __future__ import annotations
import datetime
import random
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple, Union
import heapq

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


# TASK_TYPE:
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


# 定义基础类
class Task:
    def __init__(self, task_id: int, edge_device: EdgeDevice, create_time: float,
                 input_size: int, output_size: int, process_size: int, deadline: float,
                 task_type: TaskType = TaskType.NORMAL, status: TaskStatus = TaskStatus.CREATED,
                 current_server: Optional['Server'] = None, process_server: Optional['Server'] = None,
                 current_channel: Optional['Channel'] = None,
                 upload_time: float = 0, download_time: float = 0, process_time: float = 0,
                 complete_time: float = 0, error: TaskError = TaskError.NO_ERROR,
                 tasks: List[Optional[Task]] = [], parent: Optional[Task] = None):
        self.id = task_id
        self.type = task_type
        self.edge_device = edge_device
        self.create_time = create_time
        self.current_time = create_time
        self.next_schedule_time = create_time
        self.input_size = input_size
        self.process_size = process_size
        self.output_size = output_size
        self.deadline = deadline
        self.status = status
        self.current_server = current_server
        self.process_server = process_server
        self.current_channel: Optional['Channel'] = current_channel
        self.upload_time = upload_time
        self.download_time = download_time
        self.process_time = process_time
        self.complete_time = complete_time
        self.error = error
        self.tasks = tasks  # 子任务或分片任务
        self.parent = parent  # 父任务（对于分片任务）
        self.transmit_from:Union[Server, EdgeDevice, None] = None
        self.transmit_to:Union[Server, EdgeDevice, None] = None

    def __str__(self):
        return f"Task(id={self.id}, type={self.type}, edge_device={self.edge_device.id}, create_time={self.create_time}, " \
               f"input_size={self.input_size}, process_size={self.process_size}, output_size={self.output_size}, " \
               f"deadline={self.deadline}, status={self.status}, current_server={self.current_server}, " \
               f"process_server={self.process_server}, upload_time={self.upload_time}, " \
               f"download_time={self.download_time}, process_time={self.process_time}, " \
               f"complete_time={self.complete_time}, error={self.error}, tasks={self.tasks}, parent={self.parent})\n"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.next_schedule_time < other.next_schedule_time

    def __eq__(self, other):
        if isinstance(other, Task):
            return self.id == other.id
        return False

    def update_status(self, status: TaskStatus):
        self.status = status

    def error_occurred(self, error: TaskError):
        self.error = error


# EdgeDevice：
# id：number （id）
# x：number（坐标x）
# y：number（坐标y）
# cpu_speed：number（处理性能/周期每秒）
# task_queue：Task[] （任务队列）
# move_strategy: MoveStrategy (移动策略，一个函数，待定)
class EdgeDevice:
    def __init__(self, device_id: int, x: float, y: float, cpu_speed: float = 0, task_queue: List[Task] = []):
        self.id = device_id
        self.x = x
        self.y = y
        self.cpu_speed = cpu_speed
        self.task_queue = task_queue
        self.move_strategy = None  # 移动策略，可以是一个函数，待定


# EdgeDeviceManager：
#     edge_devices: EdgeDevice[]
#     task_generate_strategy: TaskGenerateStrategy (任务生产策略，待定)
#     transmit_energy_coefficient: number (传输能量系数)
#     process_energy_coefficient: number (执行能量系数)
class EdgeDeviceManager:
    def __init__(self, edge_devices: List[EdgeDevice],
                 transmit_energy_coefficient: float = 0, process_energy_coefficient: float = 0):
        self.edge_devices = edge_devices
        self.transmit_energy_coefficient = transmit_energy_coefficient
        self.process_energy_coefficient = process_energy_coefficient
        self.task_generate_strategy = None  # 任务生成策略，可以是一个函数，待定


# Server类：
#     id：number （id）
#     children：server[] （子基站）
#     coverage：number （覆盖率/m）
#     level：number （层级，比如1就是云服务器，2就是边缘服务器，3就是边缘的边缘...）
#     x：number（坐标x）
#     y：number（坐标y）
#     cpu_speed：number（处理性能/周期每秒）
#     next_process_time: number (下次可以执行的时间)
#     memory_size: number (内存大小)
#     rest_memory: number (剩余内存)
#     task_queue：Task[]
#     ChannelManagers: dict[str,ChannelManager]
class Server:
    def __init__(self, server_id: int, children: List['Server'] = [], coverage: float = 9999, level: int = 1,
                 x: float = 0, y: float = 0, cpu_speed: float = 0, current_time: float = 0, next_process_time: float = 0,
                 memory_size: int = 0, storage_size: int = 0, rest_storage: int = 0,
                 scheduling_task_queue: List[Task] = [], to_process_task_queue: List[Task] = [], processed_task_queue: List[Task] = [],
                 cpu_utilization: float = 0.0, network_bandwidth: float = 0.0):
        self.id = server_id
        self.children = children
        self.coverage = coverage
        self.level = level
        self.x = x
        self.y = y
        self.cpu_speed = cpu_speed
        self.current_time = current_time
        self.next_process_time = next_process_time
        self.memory_size = memory_size
        self.rest_memory = memory_size
        self.storage_size = storage_size
        self.rest_storage = rest_storage
        self.scheduling_task_queue = scheduling_task_queue
        self.to_process_task_queue = to_process_task_queue
        self.processed_task_queue = processed_task_queue
        self.channel_managers: Dict[str, 'ChannelManager'] = {}
        self.cpu_utilization = cpu_utilization
        self.network_bandwidth = network_bandwidth

    def process_task(self):
        task = self.to_process_task_queue.pop()
        if task:
            process_time = max(self.next_process_time - task.current_time, 0) + task.process_size / self.cpu_speed
            self.next_process_time = max(self.next_process_time, task.current_time) + task.process_size / self.cpu_speed
            task.current_time = self.next_process_time
            task.process_time += process_time
            self.memory_size -= task.input_size
            self.memory_size += task.output_size
            self.processed_task_queue.append(task)
            self.cpu_utilization = self.calculate_cpu_utilization()

    def calculate_cpu_utilization(self) -> float:
        # Placeholder for CPU utilization calculation
        return random.uniform(0.0, 1.0)

    def allocate_resources(self, task: Task):
        # Placeholder for resource allocation logic
        pass

# ServerManager类
#     servers: Server[]
#     direct_upload_servers: Server[] (边缘设备可以直连上传的服务器)
class ServerManager:
    def __init__(self, servers: List[Server] = [], direct_upload_servers: List[Server] = []):
        self.servers = servers
        self.direct_upload_servers = direct_upload_servers

    def get_nearest_direct_upload_servers(self, x: float, y: float) -> Optional['Server']:
        nearest_servers = []
        min_distance = float('inf')
        for server in self.direct_upload_servers:
            distance = ((server.x - x) ** 2 + (server.y - y) ** 2) ** 0.5
            if distance < min_distance and distance <= server.coverage:
                min_distance = distance
                nearest_servers = [server]
            elif distance == min_distance:
                nearest_servers.append(server)
        if not nearest_servers:
            return None
        else:
            return random.choice(nearest_servers)

    def balance_load(self):
        # Placeholder for load balancing logic
        pass

    def distribute_tasks(self, tasks: List[Task]):
        # Placeholder for task distribution logic
        pass


# Channel:
#     task_queue：Task[]
#     upload_to: number (上传对象id)
#     upload_to_type: TargetType (上传对象)
#     download_from: number (下载对象id)
#     download_from_type: TargetType (下载对象)
#     next_upload_time: number (对于全双工：下次可以上传的时间)
#     next_download_time: number (对于全双工：下次可以下载的时间)
#     next_time: number (对于半双工：下次可以使用的时间)
#     next_confirmed_start_time: number (对于半双工：下次已确定任务的开始时间，即对于半双工如果后面已经有了确定的任务，
#                                       只能利用这个间隙执行其他任务，可以具体任务队列具体调度)
#     某些属性可能没啥用，之后再改
class Channel:
    def __init__(self, parent: ChannelManager = None, task_queue: List[Task] = [], upload_to: int = -1,
                 download_from: int = -1, upload_to_type: TargetType = TargetType.NO_TARGET,
                 download_from_type: TargetType = TargetType.NO_TARGET, next_upload_time: float = 0,
                 next_download_time: float = 0,
                 next_time: float = 0, next_confirmed_start_time: float = 0):
        self.parent = parent
        self.next_upload_time = next_upload_time
        self.next_download_time = next_download_time

    def set_next_upload_time(self, time:float):
        if self.parent and self.parent.is_full_duplex:
            self.next_upload_time = time
        else:
            self.next_upload_time = time
            self.next_download_time = time

    def set_next_download_time(self, time:float):
        if self.parent and self.parent.is_full_duplex:
            self.next_download_time = time
        else:
            self.next_upload_time = time
            self.next_download_time = time
# ChannelManager类：
#     channel_bandwidth： number (信道带宽/Hz)
#     M：number (信号状态数)
#     baud：number （波特率）
#     power： number （信号功率/W）
#     noise：number （噪声功率/W）
#     p/n：number （信噪比/dB，和power noise选择使用即可， = 10 * log10 p/n）
#     speed：传输速率 (一般为2.0*10^8 m/s)
#     is_full_duplex: bool (是全双工吗？)
#     is_no_noise: bool (是无噪声吗？决定奈式准则还是香农公式)
#     bandwidth: number (带宽/bps = baud * channel_bandwidth *log2(M) | channel_bandwidth * log2(1+s/n))
#     transmit_strategy: NetworkStrategy (网络策略，对于数据传输过程进行实现，具体怎么搞待定)
#
#     channels: Channel[]
#     all_bandwidth: number
#     rest_bandwidth: number
#     upload_delay: number
#     download_delay: number
class ChannelManager:
    def __init__(self, channel_bandwidth: float = 1, M: int = 64, speed: float = 2*10**8, baud: int = 2,
                 power: float = 1, noise: float = 1, p_n: float = 1,
                 is_full_duplex: bool = True, is_no_noise: bool = True,
                 channels: List[Channel] = [], bandwidth: float = 0, all_bandwidth: float = 0,
                 rest_bandwidth: float = 0, upload_delay: float = 0, download_delay: float = 0, parent:Server = None):
        self.channel_bandwidth = channel_bandwidth
        self.M = M
        self.baud = baud
        self.power = power
        self.noise = noise
        self.p_n = p_n
        self.speed = speed
        self.is_full_duplex = is_full_duplex
        self.is_no_noise = is_no_noise
        self.bandwidth = bandwidth
        self.channels = channels
        self.all_bandwidth = all_bandwidth
        self.rest_bandwidth = rest_bandwidth
        self.upload_delay = upload_delay
        self.download_delay = download_delay
        self.parent = parent
        self.transmit_strategy = None  # 网络传输策略，可以是一个函数，待定


# Scheduler：
#     time：number (当前时间，指的是模拟器内部模拟的时间)
#     edge_device_manager: EdgeDeviceManager
#     server_manager: ServerManager
#     finished_task: Task[]
#     scheduling_task: Task[] (刚生成和已完成之外的都在这里)
#     offloading_strategy: OffloadingStrategy (调度策略，选出卸载位置，具体怎么搞待定)
class Scheduler:
    def __init__(self, edge_device_manager: EdgeDeviceManager, server_manager: ServerManager):
        self.time = 0  # 使用当前时间作为初始时间
        self.edge_device_manager = edge_device_manager
        self.server_manager = server_manager
        self.finished_task: List['Task'] = []
        self.scheduling_task: List['Task'] = []
        self.offloading_strategy = None
        self.scheduling_strategy = None

    def add_task(self, task: Task):
        heapq.heappush(self.scheduling_task, task)

    def get_task(self) -> Task:
        return heapq.heappop(self.scheduling_task)

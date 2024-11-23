from module import *
import random
import numpy


# 包括任务生成策略、网络传输策略、卸载服务器选择策略、移动策略

# 服务器分为三层： 云服务器-边缘服务器-边缘子服务器
# 边缘设备只能将任务发至边缘服务器，但可以从所有服务器接收数据
# 每个服务器的通信范围为无限大
# 云服务器上传和下载无需抢占信道，可任意传输数据，内存无限，cpu假设为无限核，任何任务都可以立刻执行
# 边缘服务器与边缘子服务器之间为单条全双工信道，所有边缘设备与边缘服务器和边缘子服务器之间均为单条半双工通道
# 边缘设备的位置不变
# 边缘服务器负责卸载

class MyStrategy:
    task_category = [
        {
            "name": "AUGMENTED_REALITY",
            "percentage": 30,
            "interval": 5,
            "input_size": 1500,
            "output_size": 25,
            "process_size": 2000,
            "deadline": 3
        },
        {
            "name": "HEALTH_APP",
            "percentage": 20,
            "interval": 30,
            "input_size": 1250,
            "output_size": 20,
            "process_size": 400,
            "deadline": 2
        },
        {
            "name": "HEAVY_COMP_APP",
            "percentage": 20,
            "interval": 60,
            "input_size": 2500,
            "output_size": 250,
            "process_size": 3000,
            "deadline": 5
        },
        {
            "name": "INFOTAINMENT_APP",
            "percentage": 30,
            "interval": 7,
            "input_size": 25,
            "output_size": 2000,
            "process_size": 750,
            "deadline": 3
        }]
    server_info = {
        'count': 16,
        'memory': 8000,
        'storage': 200000,
        'cpu_speed': 4000,
        'children': {
            'count': 2,
            'memory': 2000,
            'storage': 50000,
            'cpu_speed': 1000,
        }
    }
    channel_info = {
        'server_to_server': {
            'bandwidth': 30000
        },
        'server_to_device': {
            'bandwidth': 40000
        },
        'server_to_cloud': {
            'bandwidth': 50000
        }
    }
    device_count = 400
    scheduler: Scheduler = None
    cloud_server: Server = None
    task_id = 1
    end_time = 1000

    @staticmethod
    def init():
        server_id = 1
        # 定义云服务器
        MyStrategy.cloud_server = Server(server_id, [],cpu_speed=100000, memory_size=20000000, level=1)
        server_id += 1
        MyStrategy.cloud_server.channel_managers["default"] = ChannelManager(bandwidth=50000, upload_delay=0.3,
                                                                             download_delay=0.3,
                                                                             parent=MyStrategy.cloud_server)
        MyStrategy.cloud_server.channel_managers["default"].channels.append(
            Channel(MyStrategy.cloud_server.channel_managers["default"]))
        # 定义服务器
        serverManager = ServerManager()
        for i in range(16):
            server = Server(server_id, [], x=i / 4, y=i % 4, cpu_speed=4000, memory_size=200000, level=2)
            server_id += 1
            server.channel_managers["edge_device"] = ChannelManager(bandwidth=40000, parent=server,
                                                                    is_full_duplex=False)
            server.channel_managers["edge_device"].channels.append(Channel(server.channel_managers["edge_device"]))
            for j in range(2):
                child_server = Server(server_id, [], cpu_speed=1000, memory_size=50000, level=3)
                child_server.channel_managers["parent"] = ChannelManager(bandwidth=30000, parent=child_server,
                                                                    is_full_duplex=True)
                child_server.channel_managers["parent"].channels.append(Channel(child_server.channel_managers["parent"]))
                child_server.channel_managers["edge_device"] = ChannelManager(bandwidth=40000, parent=child_server,
                                                                         is_full_duplex=False)
                child_server.channel_managers["edge_device"].channels.append(
                    Channel(child_server.channel_managers["edge_device"]))
                serverManager.servers.append(child_server)
                server.children.append(child_server)
                server_id += 1
            serverManager.servers.append(server)
            serverManager.direct_upload_servers.append(server)


        edgeDeviceManager = EdgeDeviceManager(
            [EdgeDevice(i + 1, random.random() * 4, random.random() * 4) for i in range(400)])
        scheduler = Scheduler(edgeDeviceManager, serverManager)
        MyStrategy.scheduler = scheduler

        for edgeDevice in edgeDeviceManager.edge_devices:
            edgeDevice.task_queue.append(MyStrategy.task_generate_strategy(edgeDevice, 0))

    @staticmethod
    def start():
        for edgeDevice in MyStrategy.scheduler.edge_device_manager.edge_devices:
            MyStrategy.scheduler.add_task(edgeDevice.task_queue.pop())
        MyStrategy.scheduling_strategy()


    @staticmethod
    def move_strategy(edge_device: EdgeDevice) -> Tuple[float, float]:
        return edge_device.x, edge_device.y

    @staticmethod
    def task_generate_strategy(edge_device: EdgeDevice, start_time: float = -1) -> Task:
        if start_time == -1:
            start_time = MyStrategy.scheduler.time
        # 随机0-100：
        rand = random.randint(1, 100)
        category = None
        for app in MyStrategy.task_category:
            if rand <= app["percentage"]:
                category = app
                break
            else:
                rand -= app["percentage"]
        create_time = start_time + (numpy.random.poisson(category["interval"] * 100)) / 100
        input_size = numpy.random.poisson(category["input_size"])
        output_size = numpy.random.poisson(category["output_size"])
        process_size = numpy.random.poisson(category["process_size"])
        deadline = category["deadline"] / 2 + create_time + numpy.random.poisson(category["deadline"] * 50) / 100
        MyStrategy.task_id += 1
        task = Task(MyStrategy.task_id - 1, edge_device, create_time, input_size, output_size, process_size, deadline)
        return task

    @staticmethod
    def offloading_strategy(server: Server, task: Task) -> Optional[Server]:
        target_server = None
        finish_time = 0
        # 先考虑卸载到子服务器
        for child in server.children:
            transmit_time_1 = max(child.channel_managers["parent"].channels[0].next_download_time - task.current_time,
                                  0) \
                              + task.input_size / child.channel_managers["parent"].bandwidth
            process_time = max(child.next_process_time - (task.current_time + transmit_time_1), 0) + \
                           task.process_size / child.cpu_speed
            transmit_time_2 = max(child.channel_managers["edge_device"].channels[0].next_upload_time - \
                                  (task.current_time + transmit_time_1 + process_time), 0) + \
                              task.output_size / child.channel_managers["edge_device"].bandwidth
            total_time = transmit_time_1 + process_time + transmit_time_2
            if target_server is None or total_time + task.current_time < finish_time:
                target_server = child
                finish_time = total_time + task.current_time

        # if target_server is None or finish_time > task.deadline:
        # 再看看卸载到云服务器咋样
        transmit_time_1 = task.input_size / MyStrategy.cloud_server.channel_managers["default"].bandwidth + \
                          MyStrategy.cloud_server.channel_managers["default"].download_delay
        process_time = task.process_size / MyStrategy.cloud_server.cpu_speed
        transmit_time_2 = task.output_size / MyStrategy.cloud_server.channel_managers["default"].bandwidth + \
                          MyStrategy.cloud_server.channel_managers["default"].upload_delay
        total_time = transmit_time_1 + process_time + transmit_time_2

        if target_server is None or total_time + task.current_time < finish_time:
            target_server = MyStrategy.cloud_server
            finish_time = total_time + task.current_time

        if target_server is None or finish_time > task.deadline:
            # 再看看自己运行可行不可行
            process_time = max(server.next_process_time - task.current_time, 0) + \
                           task.process_size / server.cpu_speed
            transmit_time_2 = max(server.channel_managers["edge_device"].channels[0].next_upload_time - (
                    task.current_time + process_time), 0) + \
                              task.output_size / server.channel_managers["edge_device"].bandwidth
            total_time = process_time + transmit_time_2
            if target_server is None or total_time + task.current_time < finish_time:
                target_server = server
                finish_time = total_time + task.current_time

        if target_server is None or finish_time > task.deadline:
            task.error_occurred(TaskError.REJECTED_DUE_TO_TIMEOUT)
            task.update_status(TaskStatus.REJECTED)
            return None
        return target_server

        # rand = random.randint(0,4)
        # if rand == 0:
        #     return MyStrategy.cloud_server
        # elif rand == 1:
        #     return server
        # else:
        #     return random.choice(server.children)
        # return server

    @staticmethod
    def transmit_strategy(sender: Union[Server, EdgeDevice], receiver: Union[Server, EdgeDevice], task: Task):
        if isinstance(sender, Server) and isinstance(receiver, Server):
            if receiver.level == 1:
                # 表示服务器发往云服务器
                upload_time = receiver.channel_managers["default"].download_delay + task.input_size / \
                              receiver.channel_managers["default"].bandwidth
                task.upload_time += upload_time
                task.next_schedule_time = task.current_time + upload_time
                task.process_server = receiver
                task.current_server = sender
                task.current_channel = receiver.channel_managers["default"].channels[0]
                task.status = TaskStatus.UPLOADING
                task.transmit_from = sender
                task.transmit_to = receiver
                MyStrategy.scheduler.add_task(task)
            else:
                # 表示自己运行，不卸载
                if sender == receiver:
                    process_time = max(receiver.next_process_time - task.current_time, 0) + task.process_size / receiver.cpu_speed
                    task.process_time += process_time
                    task.process_server = sender
                    task.next_schedule_time = max(receiver.next_process_time, task.current_time)
                    receiver.next_process_time += process_time
                    task.status = TaskStatus.WAIT_TO_PROCESS
                    MyStrategy.scheduler.add_task(task)
                    return
                # 表示服务器发往子服务器
                upload_time = max(
                    receiver.channel_managers["parent"].channels[0].next_download_time - task.current_time,
                    0) \
                              + task.input_size / receiver.channel_managers["parent"].bandwidth
                task.upload_time += upload_time
                task.current_server = sender
                task.process_server = receiver
                task.next_schedule_time = task.current_time + upload_time
                task.update_status(TaskStatus.UPLOADING)
                task.current_channel = receiver.channel_managers["parent"].channels[0]
                task.transmit_from = sender
                task.transmit_to = receiver
                # 内存不够是否占用传输时间，这里认为占用
                receiver.channel_managers["parent"].channels[0].set_next_download_time(task.next_schedule_time)
                receiver.rest_memory -= task.input_size
                task.transmit_from = sender
                task.transmit_to = receiver
                if receiver.rest_memory < 0:
                    receiver.rest_memory += task.input_size
                    sender.rest_memory += task.input_size
                    task.error_occurred(TaskError.REJECTED_DUE_TO_MEMORY)
                    task.update_status(TaskStatus.REJECTED)
                    MyStrategy.scheduler.finished_task.append(task)
                    return
                MyStrategy.scheduler.add_task(task)
        elif isinstance(sender, Server) and isinstance(receiver, EdgeDevice):
            if sender.level == 1:
                # 云服务器发送到边缘设备
                download_time = sender.channel_managers["default"].upload_delay + task.output_size / \
                                sender.channel_managers["default"].bandwidth
                task.download_time += download_time
                task.next_schedule_time = task.current_time + download_time
                task.status = TaskStatus.DOWNLOADING
                task.current_channel = sender.channel_managers["default"].channels[0]
                MyStrategy.scheduler.scheduling_task.append(task)
            else:
                # 边缘（子）服务器发送到边缘设备
                download_time = max(
                    sender.channel_managers["edge_device"].channels[0].next_upload_time - task.current_time,
                    0) \
                                + task.output_size / sender.channel_managers["edge_device"].bandwidth
                task.download_time += download_time
                task.next_schedule_time = max(sender.channel_managers["edge_device"].channels[0].next_upload_time,
                                              task.current_time)
                # 半双工
                sender.channel_managers["edge_device"].channels[
                    0].set_next_download_time(task.current_time + download_time)
                sender.channel_managers["edge_device"].channels[0].set_next_upload_time(task.current_time + download_time)
                task.status = TaskStatus.WAIT_TO_DOWNLOAD
                task.current_channel = sender.channel_managers["edge_device"].channels[0]
                task.current_server = sender
                task.transmit_from = sender
                task.transmit_to = task.edge_device
                MyStrategy.scheduler.add_task(task)
            task.transmit_from = sender
            task.transmit_to = receiver
        elif isinstance(sender, EdgeDevice) and isinstance(receiver, Server):
            # 必然是边缘设备发送到服务器
            upload_time = max(receiver.channel_managers["edge_device"].channels[0].next_upload_time - task.current_time,
                              0) \
                          + task.input_size / receiver.channel_managers["edge_device"].bandwidth
            task.upload_time += upload_time
            task.next_schedule_time = max(task.current_time,
                                          receiver.channel_managers["edge_device"].channels[0].next_upload_time)
            # 半双工
            receiver.channel_managers["edge_device"].channels[
                0].set_next_download_time(task.current_time + task.upload_time)
            receiver.channel_managers["edge_device"].channels[0].set_next_upload_time(task.current_time + task.upload_time)
            receiver.rest_memory -= task.input_size
            task.current_server = None
            task.current_channel = receiver.channel_managers["edge_device"].channels[0]
            task.transmit_from = sender
            task.transmit_to = receiver
            if receiver.rest_memory < receiver.memory_size / 10:
                receiver.rest_memory += task.input_size
                task.error_occurred(TaskError.REJECTED_DUE_TO_MEMORY)
                task.update_status(TaskStatus.REJECTED)
                MyStrategy.scheduler.finished_task.append(task)
                return
            task.update_status(TaskStatus.WAIT_TO_UPLOAD)
            MyStrategy.scheduler.add_task(task)

    @staticmethod
    def scheduling_strategy():
        while MyStrategy.scheduler and len(MyStrategy.scheduler.scheduling_task) > 0:
            task = MyStrategy.scheduler.get_task()
            MyStrategy.scheduler.time = task.next_schedule_time
            # 新任务，传输到服务器
            if task.status == TaskStatus.CREATED:
                if task.deadline < MyStrategy.end_time:
                    MyStrategy.scheduler.add_task(MyStrategy.task_generate_strategy(task.edge_device, task.deadline))
                nearst_server = MyStrategy.scheduler.server_manager.get_nearest_direct_upload_servers(
                    task.edge_device.x, task.edge_device.y)
                if nearst_server is None:
                    task.error_occurred(TaskError.REJECTED_DUE_TO_COVERAGE)
                    task.update_status(TaskStatus.REJECTED)
                    MyStrategy.scheduler.finished_task.append(task)
                    continue
                else:
                    MyStrategy.transmit_strategy(task.edge_device, nearst_server, task)
            # 上传中，可能为 设备->服务器 服务器->子服务器 服务器->云 云、服务器、子服务器->设备，调度到意味着上传完了
            elif task.status == TaskStatus.UPLOADING:
                task.current_time = task.next_schedule_time
                task.current_channel = None
                if isinstance(task.transmit_from, Server):
                    task.transmit_from.rest_memory += task.input_size

                if isinstance(task.transmit_from, EdgeDevice):
                    task.update_status(TaskStatus.WAIT_TO_SCHEDULE)
                    task.next_schedule_time = task.current_time
                    task.current_server = task.transmit_to
                    task.transmit_from = None
                    task.transmit_to = None
                    MyStrategy.scheduler.add_task(task)
                elif isinstance(task.transmit_to, EdgeDevice):
                    task.complete_time = task.current_time
                    task.update_status(TaskStatus.COMPLETED)
                    if task.deadline <= task.complete_time:
                        task.error_occurred(TaskError.TIMEOUT)
                    MyStrategy.scheduler.finished_task.append(task)
                elif isinstance(task.transmit_to, Server):
                    task.update_status(TaskStatus.WAIT_TO_PROCESS)
                    process_time = max(task.transmit_to.next_process_time - task.current_time, 0) + \
                                   task.process_size / task.transmit_to.cpu_speed
                    task.process_time += process_time
                    task.next_schedule_time = max(task.current_time, task.transmit_to.next_process_time)
                    task.transmit_to.next_process_time += process_time
                    task.current_server = task.transmit_to
                    task.transmit_from = None
                    task.transmit_to = None
                    MyStrategy.scheduler.add_task(task)
            # 等待卸载
            elif task.status == TaskStatus.WAIT_TO_SCHEDULE:
                target_server = MyStrategy.offloading_strategy(task.current_server, task)
                if target_server is not None:
                    MyStrategy.transmit_strategy(task.current_server, target_server, task)
                else:
                    task.current_server.rest_memory += task.input_size
                    MyStrategy.scheduler.finished_task.append(task)
            # 等待运行，但是运算时间什么的其实都已经计算好了
            elif task.status == TaskStatus.WAIT_TO_PROCESS:
                task.current_time = task.next_schedule_time
                task.next_schedule_time += task.process_size / task.current_server.cpu_speed
                task.update_status(TaskStatus.PROCESSING)
                MyStrategy.scheduler.add_task(task)
            # 正在执行的任务，调度到就是执行完了
            elif task.status == TaskStatus.PROCESSING:
                task.current_time = task.next_schedule_time
                task.process_server.rest_memory += task.input_size
                task.process_server.rest_memory -= task.output_size
                if task.process_server.rest_memory < 0:
                    task.process_server.rest_memory += task.output_size
                    task.error_occurred(TaskError.REJECTED_DUE_TO_MEMORY)
                    task.update_status(TaskStatus.REJECTED)
                    MyStrategy.scheduler.finished_task.append(task)
                    continue
                MyStrategy.transmit_strategy(task.current_server, task.edge_device, task)
            # 等待上传的任务，只能是边缘设备到服务器
            elif task.status == TaskStatus.WAIT_TO_UPLOAD:
                task.current_time = task.next_schedule_time
                assert task.current_channel is not None
                task.next_schedule_time = task.current_time + task.input_size / task.current_channel.parent.bandwidth
                task.update_status(TaskStatus.UPLOADING)
                MyStrategy.scheduler.add_task(task)
            # 等待下载的任务结果
            elif task.status == TaskStatus.WAIT_TO_DOWNLOAD:
                task.current_time = task.next_schedule_time
                assert task.current_channel is not None
                task.next_schedule_time = task.current_time + task.input_size / task.current_channel.parent.bandwidth
                task.update_status(TaskStatus.DOWNLOADING)
                MyStrategy.scheduler.add_task(task)
            # 下载的任务，调度到意味着下载完了
            elif task.status == TaskStatus.DOWNLOADING:
                task.current_time = task.next_schedule_time
                task.transmit_from.rest_memory += task.output_size
                task.current_channel = None
                task.complete_time = task.current_time
                task.update_status(TaskStatus.COMPLETED)
                if task.deadline < task.complete_time:
                    task.error_occurred(TaskError.TIMEOUT)
                MyStrategy.scheduler.finished_task.append(task)
            else:
                task.error_occurred(TaskError.UNKNOWN)
                task.update_status(TaskStatus.UNFINISHED)
                MyStrategy.scheduler.finished_task.append(task)

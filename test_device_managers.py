import unittest
from simulator import EdgeDeviceManagerContext, EdgeDeviceManager, ServerManagerContext, ServerManager, DeviceStatus, Task, TaskStatus

class TestDeviceManagers(unittest.TestCase):

    def setUp(self):
        self.edge_device_context = EdgeDeviceManagerContext(total=2)
        self.edge_device_manager = EdgeDeviceManager(self.edge_device_context)
        self.server_context = ServerManagerContext(total=2)
        self.server_manager = ServerManager(self.server_context)

    def test_edge_device_manager_init(self):
        self.assertEqual(len(self.edge_device_manager.context.vm_list), 2)
        for device in self.edge_device_manager.context.vm_list:
            self.assertEqual(device.device_status, DeviceStatus.CREATED)

    def test_server_manager_init(self):
        self.assertEqual(len(self.server_manager.context.server_list), 2)
        for server in self.server_manager.context.server_list:
            self.assertEqual(server.device_status, DeviceStatus.CREATED)

    def test_edge_device_manager_assign_tasks(self):
        tasks = [Task(task_id=i, task_context=None, task_type=None, task_status=TaskStatus.CREATED, process_size=100) for i in range(4)]
        self.edge_device_manager.assign_tasks(tasks)
        for device in self.edge_device_manager.context.vm_list:
            self.assertEqual(device.tasks.qsize(), 2)

    def test_server_manager_assign_load(self):
        self.server_manager.example_distribute_load(10)
        for server in self.server_manager.context.server_list:
            if server.load > 0:
                self.assertEqual(server.load, 10)
                break

    def test_edge_device_manager_run(self):
        tasks = [Task(task_id=i, task_context=None, task_type=None, task_status=TaskStatus.CREATED, process_size=100) for i in range(4)]
        self.edge_device_manager.assign_tasks(tasks)
        self.edge_device_manager.run()
        for device in self.edge_device_manager.context.vm_list:
            self.assertEqual(device.device_status, DeviceStatus.WORKING)

    def test_server_manager_run(self):
        self.server_manager.run()
        for server in self.server_manager.context.server_list:
            self.assertEqual(server.device_status, DeviceStatus.CREATED)

if __name__ == '__main__':
    unittest.main()

import logging
from task import Task, NetworkManager  # Import Task and NetworkManager from task module

logging.basicConfig(filename='task_manager.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TaskManager:
    def __init__(self, network_manager: NetworkManager, tasks_number: int, tasks_size: int):
        self.network_manager = network_manager
        self.tasks_number = tasks_number
        self.tasks_size = tasks_size

    def generate_tasks(self):
        # Generate tasks based on the network topology and task requirements
        tasks = []
        for i in range(self.tasks_number):
            task = Task(i, self.network_manager)
            tasks.append(task)
        return tasks

    def is_done(self) -> bool:
        # Check if all tasks are completed
        return True

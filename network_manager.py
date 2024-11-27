"""
Network Manager class.
"""
import random
import logging
from context import EdgeDeviceManagerContext, ServerManagerContext  # Import EdgeDeviceManagerContext and ServerManagerContext from context module

logging.basicConfig(level=logging.INFO)

class NetworkManager:
    def __init__(self, edge_device_context: EdgeDeviceManagerContext, server_context: ServerManagerContext):
        self.edge_device_context = edge_device_context
        self.server_context = server_context

    def get_edge_device_info(self, device_id):
        return self.edge_device_context.vm_list[device_id]

    def get_server_info(self, device_id):
        return self.server_context.server_list[device_id]

    def get_device_info(self, device_id):
        if device_id in self.edge_device_context.vm_list:
            return self.edge_device_context.vm_list[device_id]
        elif device_id in self.server_context.server_list:
            return self.server_context.server_list[device_id]
        else:
            return None

    def get_frequency(self, device_id):
        return random.randint(100, 1000)

    def assign_frequency(self, device_id, frequency):
        pass

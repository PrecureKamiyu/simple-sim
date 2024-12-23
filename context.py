"""
Context class.
"""
from __future__ import annotations
import random
import logging
from device import EdgeDevice, Server  # Import EdgeDevice and Server from device module

logging.basicConfig(filename='context.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EdgeDeviceManagerContext:

    def __init__(self, total: int):
        self.vm_list: list = []
        self.total = total

    def init(self):
        global global_device_id_counter
        # create vm_list
        for _ in range(self.total):
            self.vm_list.append(EdgeDevice(global_device_id_counter))
            global_device_id_counter += 1


class ServerManagerContext:

    def __init__(self, total: int):
        self.server_list: list = []
        self.total = total

    def init(self):
        global global_device_id_counter
        # create server list here
        for _ in range(self.total):
            self.server_list.append(Server(global_device_id_counter, x=random.uniform(0, 100), y=random.uniform(0, 100), coverage_range=random.uniform(0, 100)))
            global_device_id_counter += 1

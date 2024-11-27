"""
Edge Device Manager Context class.
"""
from __future__ import annotations
from enum import Enum
import random
from typing import Optional, List
import logging
from queue import Queue
from device import EdgeDevice  # Import EdgeDevice from device module
from context import EdgeDeviceManagerContext, ServerManagerContext  # Import EdgeDeviceManagerContext and ServerManagerContext from context module

logging.basicConfig(filename='edge_device_manager_context.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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

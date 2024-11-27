"""
Server Manager Context class.
"""
from __future__ import annotations
from enum import Enum
import random
from typing import Optional, List
import logging
from queue import Queue
from device import Server

logging.basicConfig(filename='server_manager_context.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ServerManagerContext:

    def __init__(self, total: int):
        self.server_list: list[Server] = []
        self.total = total

    def init(self, server_manager: ServerManager):
        global global_device_id_counter
        # create server list here
        for _ in range(self.total):
            self.server_list.append(Server(global_device_id_counter, x=random.uniform(0, 100), y=random.uniform(0, 100), coverage_range=random.uniform(0, 100)))
            global_device_id_counter += 1

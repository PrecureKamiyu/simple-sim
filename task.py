"""
Task class.
"""
from __future__ import annotations
from enum import Enum
import random
from typing import Optional, List
import logging
from queue import Queue

logging.basicConfig(filename='task.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TaskType(Enum):
    NORMAL = "NORMAL"
    # Add other task types as needed


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

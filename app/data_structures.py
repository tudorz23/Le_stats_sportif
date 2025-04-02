"""
Module that offers useful data structures for threadpool task queue managing.
"""

from enum import Enum, auto

class TaskType(Enum):
    """
    Contains the supported task types.
    """
    STATES_MEAN = auto()
    STATE_MEAN = auto()
    BEST5 = auto()
    WORST5 = auto()
    GLOBAL_MEAN = auto()
    DIFF_FROM_MEAN = auto()
    STATE_DIFF_FROM_MEAN = auto()
    MEAN_BY_CATEGORY = auto()
    STATE_MEAN_BY_CATEGORY = auto()
    SHUTDOWN = auto()
    CSV_PARSE = auto()


class Task:
    """
    Encapsulates information regarding a task.
    """
    def __init__(self, task_id = -1, question = None, state = None, task_type = None):
        self.task_id = task_id
        self.question = question
        self.state = state
        self.task_type = task_type

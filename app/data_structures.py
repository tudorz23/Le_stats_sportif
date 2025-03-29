from enum import Enum, auto

class TaskType(Enum):
    STATES_MEAN = auto()
    STATE_MEAN = auto()
    BEST5 = auto()
    WORST5 = auto()
    GLOBAL_MEAN = auto()
    DIFF_FROM_MIN = auto()
    STATE_DIFF_FROM_MEAN = auto()
    MEAN_BY_CATEGORY = auto()
    STATE_MEAN_BY_CATEGORY = auto()
    SHUTDOWN = auto()


class Task:
    def __init__(self, question = None, state = None, task_type = None):
        self.question = question
        self.state = state
        self.task_type = task_type

from queue import Queue
from threading import Thread, Event, Lock
import time
import os
import data_structures as d_s

class ThreadPool:
    def __init__(self, data_ingestor):
        self.ing = data_ingestor
        self.job_counter = 1

        # Status of a job: running/done
        self.jobs_status = {}

        # The main thread puts tasks in this queue, the workers get from it.
        self.tasks_queue = Queue() # synchronized

        # Event to know when the server received graceful_shutdown
        self.is_shutdown = Event()

        self.nr_workers = ThreadPool.get_nr_workers()
        self.workers = [TaskRunner(self.tasks_queue, self.ing) for _ in range(self.nr_workers)]

        # Start the threads
        for worker in self.workers:
            worker.start()


    @staticmethod
    def get_nr_workers():
        nr_workers = os.getenv("TP_NUM_OF_THREADS")
        if nr_workers is not None:
            return int(nr_workers)

        return os.cpu_count()


    def enqueue_task(self, task: d_s.Task):
        """" Adds a task to the queue and returns its job_id """
        job_id = self.job_counter
        self.jobs_status[job_id] = "running"
        self.tasks_queue.put(task)

        # Increment job_counter
        self.job_counter += 1

        return job_id


    def get_job_status(self, job_id):
        """"
        Checks if the job is valid. Returns None if invalid, status if valid.
        """
        if job_id <= 0 or self.job_counter <= job_id:
            return None

        return self.jobs_status[job_id]


    def manage_shutdown(self):
        """" Announces the workers to shut down """
        self.is_shutdown.set()

        # Add SHUTDOWN tasks in the queue, one for each worker
        for i in range(self.nr_workers):
            sh_task = d_s.Task(task_type=d_s.TaskType.SHUTDOWN)
            self.tasks_queue.put(sh_task)

        # Wait for the workers to finish
        for worker in self.workers:
            worker.join()


class TaskRunner(Thread):
    def __init__(self, tasks_queue, data_ingestor):
        super().__init__()
        self.tasks_queue = tasks_queue
        self.data_ingestor = data_ingestor


    def run(self):
        while True:
            # Blocking get() call
            task: d_s.Task = self.tasks_queue.get()

            if task.task_type == d_s.TaskType.SHUTDOWN:
                return

            self.execute_task(task)

    def execute_task(self, task: d_s.Task):
        pass
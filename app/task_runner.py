"""
Module that manages the ThreadPool and its Workers.
"""

import json
from queue import Queue
from threading import Thread, Event, Lock
import os
from app import data_structures as d_s

class ThreadPool:
    """
    Adds jobs to the queue and controls the start and the shutdown.
    """
    def __init__(self, data_ingestor):
        self.data_ing = data_ingestor
        self.job_counter = 1

        # Status of a job: running/done
        self.jobs_status = {}

        # The main thread puts tasks in this queue, the workers get from it.
        self.tasks_queue = Queue() # synchronized

        # Event to know when the server received graceful_shutdown
        self.is_shutdown = Event()

        # Event to know when the parsing of the csv of the ingestor is finished
        self.csv_ready = Event()

        # Lock for accessing the job_counter.
        self.counter_lock = Lock()

        self.nr_workers = ThreadPool.get_nr_workers()
        self.workers = [TaskRunner(self.tasks_queue, self.data_ing, self.jobs_status,
                                   self.csv_ready) for _ in range(self.nr_workers)]

        # Start the threads
        for worker in self.workers:
            worker.start()

        # Enqueue a task for csv file parsing (before receiving any web request task!)
        self.tasks_queue.put(d_s.Task(task_type=d_s.TaskType.CSV_PARSE))


    @staticmethod
    def get_nr_workers():
        """
        Computes the number of workers to be started.
        """
        nr_workers = os.getenv("TP_NUM_OF_THREADS")
        if nr_workers is not None:
            return int(nr_workers)

        return os.cpu_count()


    def get_next_job_id_and_increment(self):
        """
        Returns the id of the next job (i.e. job_counter) and increments the job_counter.
        """
        with self.counter_lock:
            next_id = self.job_counter
            self.job_counter += 1
        return next_id


    def enqueue_task(self, task: d_s.Task):
        """
        Adds a task to the queue.
        """
        self.jobs_status[task.task_id] = "running"
        self.tasks_queue.put(task)


    def get_job_status(self, job_id):
        """
        Checks if the job is valid. Returns None if invalid, status if valid.
        """
        ok = True
        with self.counter_lock:
            if job_id <= 0 or self.job_counter <= job_id:
                ok = False

        return None if not ok else self.jobs_status[job_id]


    def manage_shutdown(self):
        """
        Announces the workers to shut down.
        """
        self.is_shutdown.set()

        # Add SHUTDOWN tasks in the queue, one for each worker
        for _ in range(self.nr_workers):
            sh_task = d_s.Task(task_type=d_s.TaskType.SHUTDOWN)
            self.tasks_queue.put(sh_task)

        # Wait for the workers to finish
        for worker in self.workers:
            worker.join()


class TaskRunner(Thread):
    """
    Gets jobs from the queue and executes them until it receives a shutdown job.
    """
    def __init__(self, tasks_queue, data_ingestor, jobs_status, csv_ready: Event):
        super().__init__()
        self.tasks_queue = tasks_queue
        self.data_ingestor = data_ingestor
        self.jobs_status = jobs_status
        self.csv_ready = csv_ready


    def run(self):
        """
        Infinite loop to get tasks from the queue and execute them. Stops at SHUTDOWN.
        """
        while True:
            # Blocking get() call
            task: d_s.Task = self.tasks_queue.get()

            # If it is shutdown, halt execution immediately
            if task.task_type == d_s.TaskType.SHUTDOWN:
                return

            # If it is csv_parse, do it and notify everyone else
            if task.task_type == d_s.TaskType.CSV_PARSE:
                self.data_ingestor.populate_database()
                self.csv_ready.set()
                continue

            # Wait until the csv parsing is complete
            self.csv_ready.wait()

            result = self.execute_task(task)

            # Write the result on the disk
            target_file = f"results/{task.task_id}.json"
            with open(target_file, "w", encoding="utf-8") as json_file:
                json.dump(result, json_file)

            self.jobs_status[task.task_id] = "done"


    def execute_task(self, task: d_s.Task):
        """
        Computes the results for the task, using methods from data_ingestor.
        """
        if task.task_type == d_s.TaskType.STATES_MEAN:
            result = self.data_ingestor.compute_states_mean(task.question)
        elif task.task_type == d_s.TaskType.STATE_MEAN:
            result = self.data_ingestor.compute_state_mean(task.question, task.state)
        elif task.task_type == d_s.TaskType.BEST5:
            result = self.data_ingestor.compute_best5(task.question)
        elif task.task_type == d_s.TaskType.WORST5:
            result = self.data_ingestor.compute_worst5(task.question)
        elif task.task_type == d_s.TaskType.GLOBAL_MEAN:
            result = self.data_ingestor.compute_global_mean(task.question)
        elif task.task_type == d_s.TaskType.DIFF_FROM_MEAN:
            result = self.data_ingestor.compute_diff_from_mean(task.question)
        elif task.task_type == d_s.TaskType.STATE_DIFF_FROM_MEAN:
            result = self.data_ingestor.compute_state_diff_from_mean(task.question, task.state)
        elif task.task_type == d_s.TaskType.MEAN_BY_CATEGORY:
            result = self.data_ingestor.compute_mean_by_category(task.question)
        elif task.task_type == d_s.TaskType.STATE_MEAN_BY_CATEGORY:
            result = self.data_ingestor.compute_state_mean_by_category(task.question, task.state)
        else:
            result = {"error" : "What are you even doing?"}

        return result

*Designed by Marius-Tudor Zaharia, 333CA, March 2025*

# Le Stats Sportif

---

## Table of contents
1. [What is Le Stats Sportif?](#what-is-le-stats-sportif)
2. [File distribution](#file-distribution)
3. [Running](#running)
4. [General details](#general-details)
5. [Implementation details](#implementation-details)
6. [Logging](#logging)
7. [Unit tests](#unit-tests)
8. [Final thoughts](#final-thoughts)
9. [Bibliography](#bibliography)

---

## What is Le Stats Sportif?
* **Le Stats Sportif** is an implementation of a basic multithreaded webserver,
using the `Flask` Python framework.
* The role of the server is to provide statistics regarding a dataset to the
clients. Internally, it implements a ThreadPool that manages a queue of tasks,
with multiple workers extracting and executing those tasks in parallel.
* The dataset is in the `.csv` format, while the server relies on the `.json`
format to communicate with the clients.

---

## File distribution
* The `app` module contains the server implementation, as follows:
    * `data_ingestor.py` for the data managing class, `DataIngestor`
    * `routes.py` for the web routes and the actions for each
    * `task_runner.py` for the `ThreadPool` and the `Workers`
    * `data_structures.py` for useful data structures used in the implementation
* The `unittests` module contains a testing class for validating the calculations
executed by the methods of the `DataIngestor` class.

---

## Running
* A virtual environment should firstly be created, using `make create_venv`.
* After creating the venv and installing the requirements, the server can be
started using `make run_server`. Some pre-defined tests can be run from a
different terminal using `make run_tests`.

---

## General details
* The requests, in the `Flask` model, are received when a client is accessing a
`route` of the website.
* Then, the server, through the `ThreadPool`, creates a new `job` and adds it to
a `queue`, returning the `job_id` to the client.
* The client can use that id to further query the server regarding the state of
that job (i.e. `running/done`), and to receive the results when it is done.
* In the meanwhile, the `worker` threads extract a task from the queue and, after
executing it, store the results on the server disk, in a `.json` file with the
`job_id` as the name, ready to be sent to a client that is asking.
* When the server receives a `graceful_shutdown` request, it stops taking new jobs,
but still finishes the ones that are already in the queue. It then signals each
worker to shut down and responds only to requests regarding already finished jobs
(i.e. `get_results`, `jobs`, `num_jobs`).

---

## Implementation details
* The `DataIngestor` parses the `.csv` file and stores the data grouped by the
question, then by the state, and finally, for each tuple of stratifications, the
values registered for them.
* The `ThreadPool` uses a `queue.Queue()` for the tasks queue, which is synchronized,
so all the threads can call `put()` and `get()` on it with no race condition.
* To know when the `shutdown` request was received in order to stop adding new tasks,
an `Event` variable is used (could have also been done just as well using a boolean
and a `Lock`).
* As it is unclear if multiple requests can be processed in parallel (i.e. if Flask
somehow creates multiple threads under the hood to handle simultaneous requests), a
`Lock` variable is used to safeguard the `job_counter` (which might be the subject of
a race condition if so).
* To make it crystal-clear what is added to the queue, a `Task` class is used, which
encapsulates the details regarding a job. The workers identify what kind of task it is
by the `TaskType` enum attribute. This is also how the ThreadPool announces them when
it is time to shut down: it enqueues `nr_workers` jobs of `SHUTDOWN` type. When a
worker decodes such a job, it immediately halts its execution. Thus, it is certain that
every worker will eventually extract such a job from the queue.

---

## Logging
* A logging mechanism is used for writing to a file the important events taking place
with the server.
* The `logger` module is used, alongside a `RotatingFileHandler` for efficiently storing
the logs and a `Formatter` to print the time in `GMT` standard.

---

## Unit tests
* The `TestWebserver` class is used for testing the computational results of the
`DataIngestor` methods, using a smaller, more manageable subset of the data provided
in the original `.csv`.
* To run the tests, `python3 -m unittest -v unittests/TestWebserver.py` should be invoked
from the root of the project.

---

## Final thoughts
* I encountered some problems while working at the unit tests:
  * The `DataIngestor` is in the `app` module, so, when importing it, the `__init.py__`
    of `app` is also run, which starts the server. It is not a severe problem, as the
    tests run just fine, but the server continues to run at the end. It should be stopped
    by a `CTRL+C`.
  * I used `numpy.average()` when computing various statistics in the `DataIngestor`.
    When comparing the reference values (added by me) with the result from the ingestor,
    I found out that it had some `np.float64` variables, which made the assertion fail.
    I had to change the compute methods to cast those values to a basic `float`. Strange,
    but at least I learnt something new.
* I used `DeepDiff` for dictionary comparisons (as used in the official checker). It is nice
that it allows to set a custom tolerance.
* To simulate the `graceful_shutdown` request, I accessed its associated route from the
browser (from the url suggested in the terminal when starting the server).
* Finally, the implementation passes all the tests and I believe it conforms to all the
constraints of the project.

---

## Bibliography
* [CSV parsing](https://www.geeksforgeeks.org/reading-csv-files-in-python/)
* [filter() in Python](https://www.geeksforgeeks.org/filter-in-python/)
* [Flask Hello world](https://www.youtube.com/watch?v=mqhxxeeTbu0&list=PLzMcBGfZo4-n4vJJybUVV3Un_NFS5EOgX&index=1)
* [Enums in Python](https://docs.python.org/3/howto/enum.html)
* JSON [dump](https://www.geeksforgeeks.org/json-dump-in-python/) and
  [load](https://www.geeksforgeeks.org/json-load-in-python/)
* [Mean with np.average()](https://www.geeksforgeeks.org/find-average-list-python/)
* [Logging](https://docs.python.org/3/howto/logging.html)
* [Unittests](https://docs.python.org/3/library/unittest.html)
* [Comparing dictionaries](https://flexiple.com/python/python-compare-two-dictionaries)
  and [DeepDiff](https://zepworks.com/deepdiff/current/diff.html)
* Finally, the [2nd](https://ocw.cs.pub.ro/courses/asc/laboratoare/02) and
  [3rd](https://ocw.cs.pub.ro/courses/asc/laboratoare/03) ASC labs.





  
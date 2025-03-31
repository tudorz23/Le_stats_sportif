"""
Module that defines the routes for the requests that the server will answer to.
"""

import json
from flask import request, jsonify
from app import webserver
from app import data_structures as d_s


def create_task(data, task_type: d_s.TaskType):
    """
    Builds a Task for a statistics request (i.e contains a question).
    """
    # Check if the server is shutting down
    if webserver.tasks_runner.is_shutdown.is_set():
        webserver.logger.error("Cannot create new tasks, server is shutting down!")
        return jsonify( {"status" : "error", "reason" : "shutting down"} )

    # Create task and pass it to the threadpool
    if "question" in data:
        question = data["question"]
    else:
        webserver.logger.error("You should attach a question to your request!")
        return jsonify( {"status": "error", "reason": "where is your question?"} )

    state = data["state"] if "state" in data else None

    job_id = webserver.tasks_runner.get_next_job_id_and_increment()
    task = d_s.Task(job_id, question, state, task_type)
    webserver.tasks_runner.enqueue_task(task)

    webserver.logger.info("Added job %s to the tasks queue.", job_id)
    return jsonify( {"job_id": job_id} )

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """
    Route for the states_mean request.
    """
    # Get request data
    data = request.json
    webserver.logger.info("Received /api/states_mean request.")
    return create_task(data, d_s.TaskType.STATES_MEAN)

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """
    Route for the state_mean request.
    """
    # Get request data
    data = request.json
    webserver.logger.info("Received /api/state_mean request.")
    return create_task(data, d_s.TaskType.STATE_MEAN)

@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """
    Route for the best5 request.
    """
    # Get request data
    data = request.json
    webserver.logger.info("Received /api/best5 request.")
    return create_task(data, d_s.TaskType.BEST5)

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """
    Route for the worst5 request.
    """
    # Get request data
    data = request.json
    webserver.logger.info("Received /api/worst5 request.")
    return create_task(data, d_s.TaskType.WORST5)

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    """
    Route for the global_mean request.
    """
    # Get request data
    data = request.json
    webserver.logger.info("Received /api/global_mean request.")
    return create_task(data, d_s.TaskType.GLOBAL_MEAN)

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    """
    Route for the diff_from_min request.
    """
    # Get request data
    data = request.json
    webserver.logger.info("Received /api/diff_from_mean request.")
    return create_task(data, d_s.TaskType.DIFF_FROM_MEAN)

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    """
    Route for the state_diff_from_mean request.
    """
    # Get request data
    data = request.json
    webserver.logger.info("Received /api/state_diff_from_mean request.")
    return create_task(data, d_s.TaskType.STATE_DIFF_FROM_MEAN)

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """
    Route for the mean_by_category request.
    """
    # Get request data
    data = request.json
    webserver.logger.info("Received /api/mean_by_category request.")
    return create_task(data, d_s.TaskType.MEAN_BY_CATEGORY)

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """
    Route for the state_mean_by_category request.
    """
    # Get request data
    data = request.json
    webserver.logger.info("Received /api/state_mean_by_category request.")
    return create_task(data, d_s.TaskType.STATE_MEAN_BY_CATEGORY)

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown_request():
    """
    Route for the graceful_shutdown request.
    """
    # Check if there are still jobs in the queue.
    still_processing = not webserver.tasks_runner.tasks_queue.empty()

    webserver.logger.info("Received /api/graceful_shutdown request.")

    # Notify the threadpool about the shutdown
    webserver.tasks_runner.manage_shutdown()

    webserver.logger.info("Webserver is shutting down.")

    if still_processing:
        return jsonify( {"status" : "running"})
    return jsonify( {"status" : "done"})

@webserver.route('/api/jobs', methods=['GET'])
def get_all_jobs_request():
    """
    Return al job_id's, with their current status (running/done).
    """
    webserver.logger.info("Received /api/jobs request.")

    response = {"status": "done", "data": []}

    for i in range(1, webserver.tasks_runner.job_counter):
        job_id = f"job_id_{i}"
        response["data"].append( {job_id, webserver.tasks_runner.jobs_status[i]} )

    return jsonify(response)

@webserver.route('/api/num_jobs', methods=['GET'])
def get_num_jobs_request():
    """
    Return the number of jobs which are currently running
    """
    webserver.logger.info("Received /api/num_jobs request.")

    running_jobs = len(list(filter(
            lambda status: status == "running", webserver.tasks_runner.jobs_status.values())))

    webserver.logger.info("There are %s jobs currently running.", running_jobs)
    return jsonify( {"num_jobs" : running_jobs} )

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    """
    Route for the get_results request.
    """
    job_id = int(job_id)
    webserver.logger.info("Received /api/get_results request for job %s.", job_id)

    status = webserver.tasks_runner.get_job_status(job_id)
    if status is None:
        webserver.logger.error("The requested job_id, %s, is invalid!", job_id)
        return jsonify( {"status" : "error", "reason" : "Invalid job_id"} )

    if status == "running":
        webserver.logger.info("Job %s is currently running.", job_id)
        return jsonify( {"status" : "running"} )

    # Here, status == "done"
    webserver.logger.info("Job %s is done.", job_id)

    # Load result from file
    target_file = f"results/{job_id}.json"
    with open(target_file, "r", encoding="utf-8") as res_file:
        result_json = json.load(res_file)

    return jsonify( {"status" : "done", "data" : result_json} )

# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    """
    Route for the main page of the website.
    """
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

def get_defined_routes():
    """
    Helper to get all the available routes from the website.
    """
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes

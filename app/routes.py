from app import webserver
from flask import request, jsonify

import os
import json

import data_structures as d_s


def create_task(data, task_type: d_s.TaskType):
    """" Builds a Task for a statistics request (with a question) """
    # Check if the server is shutting down
    if webserver.tasks_runner.is_shutdown.is_set():
        jsonify( {"status" : "error", "reason" : "shutting down"} )

    # Create task and pass it to the threadpool
    question = None
    if "question" in data:
        question = data["question"]
    else:
        jsonify( {"status": "error", "reason": "where is your question?"} )

    state = None
    if "state" in data:
        state = data["state"]

    task = d_s.Task(question, state, task_type)

    job_id = webserver.tasks_runner.enqueue(task)
    return jsonify( {"job_id": job_id} )


@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    # Get request data
    data = request.json
    return create_task(data, d_s.TaskType.STATES_MEAN)

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    # Get request data
    data = request.json
    return create_task(data, d_s.TaskType.STATE_MEAN)

@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    # Get request data
    data = request.json
    return create_task(data, d_s.TaskType.BEST5)

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    # Get request data
    data = request.json
    return create_task(data, d_s.TaskType.WORST5)

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    # Get request data
    data = request.json
    return create_task(data, d_s.TaskType.GLOBAL_MEAN)

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    # Get request data
    data = request.json
    return create_task(data, d_s.TaskType.DIFF_FROM_MIN)

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    # Get request data
    data = request.json
    return create_task(data, d_s.TaskType.STATE_DIFF_FROM_MEAN)

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    # Get request data
    data = request.json
    return create_task(data, d_s.TaskType.MEAN_BY_CATEGORY)

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    # Get request data
    data = request.json
    return create_task(data, d_s.TaskType.STATE_MEAN_BY_CATEGORY)

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown_request():
    # Check if there are still jobs in the queue.
    still_processing = not webserver.tasks_runner.tasks_queue.empty()

    # Notify the threadpool about the shutdown
    webserver.tasks_runner.manage_shutdown()

    if still_processing:
        return jsonify( {"status" : "running"})
    return jsonify( {"status" : "done"})

@webserver.route('/api/jobs', methods=['GET'])
def get_all_jobs_request():
    """" Return al job_id's with their current status (running/done) """
    response = {"status": "done", "data": []}

    for i in range(1, webserver.tasks_runner.job_counter):
        job_id = "job_id_{}".format(i)
        response["data"].append( {job_id, webserver.tasks_runner.jobs_status[i]} )

    return jsonify(response)

@webserver.route('/api/num_jobs', methods=['GET'])
def get_num_jobs_request():
    """" Return the number of jobs which are currently running """
    running_jobs = list(filter(lambda x: x == "running", webserver.tasks_runner.jobs_status))
    return jsonify( {"num_jobs" : len(running_jobs)})


@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    status = webserver.tasks_runner.get_job_status(job_id)
    if status is None:
        return jsonify( {"status" : "error", "reason" : "Invalid job_id"} )

    if status == "running":
        return jsonify( {"status" : "running"})

    # status == "done"
    # Load result from file
    target_file = "results/{}.json".format(job_id)
    with open(target_file, 'r', encoding='utf-8') as res_file:
        result_json = json.load(res_file)

    return jsonify( {"status" : "done", "data" : result_json})


# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    routes = get_defined_routes()
    msg = f"Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

def get_defined_routes():
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes

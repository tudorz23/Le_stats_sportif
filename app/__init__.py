"""
Module that initializes the necessary entities for the running of the webserver.
"""

import os
import time
import logging
import logging.handlers as handle
from logging import DEBUG
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

if not os.path.exists('results'):
    os.mkdir('results')

# Create server
webserver = Flask(__name__)

# Initialize logging stuff: logger gets a handler, who gets a formatter

# Set formatter
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')
formatter.converter = time.gmtime

# Set handler to maximum 64KB
handler = handle.RotatingFileHandler(filename='webserver.log', maxBytes=65536,
                                     backupCount=3, encoding='utf-8')
handler.setLevel(DEBUG)
handler.setFormatter(formatter)

# Set logger
webserver.logger = logging.getLogger('webserver_logger')
webserver.logger.setLevel(DEBUG)
webserver.logger.addHandler(handler)

# Initialize data ingestor
webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

# Initialize ThreadPool
webserver.tasks_runner = ThreadPool(webserver.data_ingestor)

webserver.logger.info("====== Server is on, here we go! ======\n")

from app import routes

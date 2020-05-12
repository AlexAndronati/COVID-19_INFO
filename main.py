import random
import string
import json
import logging
import time

# import daemon
from logging.handlers import RotatingFileHandler

from data_worker import DataWorker

from flask import Flask, render_template, request

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# logging.basicConfig(filename='logs/countries.log', level=logging.DEBUG)

def init_app_logger():
    handler = RotatingFileHandler(
        'logs/countries.log', maxBytes=10_000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} '
        '%(levelname)s - %(message)s'
    )
    handler.setFormatter(file_formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    init_app_logger()
    with app.app_context():
        import routes
    app.run()


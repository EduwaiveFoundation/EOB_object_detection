from celery import shared_task, task
import time
from services import *

@shared_task
def predictions(*args):
    print ("Job started")
    time.sleep(10)
    return "Job done..."


def object_detection(*args):
    pass


def ocr():
    pass
from celery import shared_task, task
import time
from services import classification_pred
from env_var import *

@shared_task
def predictions(*args):
    print ("Job started")
    time.sleep(10)
    img_path=IMAGE_PATH
    image_label=classification_pred.main(img_path) 
    return "Job done..."


def object_detection(*args):
    pass


def ocr():
    pass
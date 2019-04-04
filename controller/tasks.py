from celery import shared_task, task
from celery.utils.log import get_task_logger
from celery import current_task
import time
from services import classification_pred,object_detection_pred
from vars_ import *

logger = get_task_logger(__name__)

@shared_task
def predictions(*args):
    print ("Job started")
    #time.sleep(10)
    img_path=IMAGE_PATH
    #print(img_path)
    image_label=classification_pred.main(img_path)
    bucket=img_path.replace("gs://","").split("/")[0]
    folder=img_path.replace("gs://","").split("/",1)[-1]
    #print (folder)
    #path to images to be classified
    images_path=classification_pred.list_blobs(bucket,folder)
    current_task.update_state(state='PROGRESS',
            meta={'stage': 'Downloading files from gcs'})
    images_path=classification_pred.download_blob(bucket,images_path)
    #print images_path
    logger.info("\nFiles Downloaded")
    #image_dictionary gives key as path to image and value as its array
    image_dictionary={}
    current_task.update_state(state='PROGRESS',
            meta={'stage':'converting images into desired format'})
    for image in images_path:
        image_dictionary[image] = classification_pred._path_to_img(image)
    logger.info("\nImages converted into desired format")    

    #TODO
    #need to write a function which automatically used latest model from the model_directory
    #path to saved model
    export_dir = STAGING_AREA+"/"+CLASSIFICATION_MODEL_DIR 
    current_task.update_state(state='PROGRESS',
            meta={'stage':'predicting classes'})
    #make_predictions
    output=classification_pred.prediction(export_dir,image_dictionary) 
    #print (output)
    #image_label gives path to image with its label
    #print output
    image_label={key:(CLASSIFICATION_LABEL_USEFUL if value < 0 else CLASSIFICATION_LABEL_NOT_USEFUL) for key,value in                  zip(image_dictionary.keys(), output) } 

    logger.info("\nClassification prediction pipeline completed")
    #print (image_label)
    image_path.append((key if value==CLASSIFICATION_LABEL_USEFUL)for key,values in dictionary.items())
    print image_path
    
    #print ("job done")
    #image_label=classification_pred.main(img_path) 
    return "Job done..."

@task
def object_detection(*args):
    print "object detection prediction started"
    object_detection_pred.main()
    print "prediction completed"
    pass


def ocr():
    pass
from celery import shared_task, task
from celery.utils.log import get_task_logger
from celery import current_task
import time
from services import classification_pred,object_detection_pred,ocr_eob,move_files
from services.db_connector import DataStore

from vars_ import *

logger = get_task_logger(__name__)

# Init Database
# Specify KIND = ocr
db = DataStore(kind='ocr')

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
    image_label={key:(CLASSIFICATION_LABEL_NOT_USEFUL if value < 0 else CLASSIFICATION_LABEL_USEFUL) for key,value in                  zip(image_dictionary.keys(), output) } 

    logger.info("\nClassification prediction pipeline completed")
    #print (image_label)
    image_path=[]
    for key,value in image_label.items():    # for name, age in dictionary.iteritems():  (for Python 2.x)
        if value == CLASSIFICATION_LABEL_USEFUL:
            image_path.append(key)
    object_detection(image_path)        
    
    #print ("job done")
    #image_label=classification_pred.main(img_path) 
    return "Job done..."

@task
def object_detection(*args):
    print "object detection prediction started"
    category_index,bb_info=object_detection_pred.main(args[0])
    #print category_index
    #print ocr
    print "object detection prediction completed"
    ocr(bb_info,category_index)
    pass


@shared_task
def ocr(*args):
    """
    Perform OCR and push to DataStore
    """
    print "ocr started"
    ocr_data=ocr_eob.main(args[0],args[1])
    print ocr_data
    for data in ocr_data:
        db.post(data)
    print "ocr ended"
    move()
    # Perform OCR
    
    #############################
    # PUSH TO DATASTORE
    # Example 
    # data = {
    #        "Filename" : "labelled/2019-04-04/3.jpg", #String (Mandatory) and should be path \
    #                                                           in ref to GCS path after bucket name
    #        "PatientName" : "Kent Strip",             #String
    #        "BilledAmount" : "260",                   #Float
    #        "CheckDate" : "01/03/18",                 #String 
    #        "Claim#" : "3240956928485096",            #String
    #     }
    # More fields could be added...
    # db.push(data)
    #############################
    pass

@shared_task
def move(*args):
    print "moving files to labelled"
    move_files.main()
    print "files moved to labelled folder"
    
from celery import shared_task, task
from celery.utils.log import get_task_logger
from celery.result import AsyncResult
from celery import current_task
from celery import subtask
import time, os
import codecs, json 
from services import classification_pred,object_detection_pred,ocr_eob,move_files, eob_type
from services.db_connector import DataStore
import shutil
from vars_ import *
from multiprocessing import Queue

import time

logger = get_task_logger(__name__)
TASK_ID=[]
# Init Database
# Specify KIND = ocr
db = DataStore(kind='ocr')

# Specify KIND = img_name for pushing bounding box data in datastore
db2 = DataStore(kind='img_name')
IMAGE_PATH = Queue() 

#@shared_task
def predictions(*args):
    print ("Job started")
    #time.sleep(10)
    img_path=args[0]
    IMAGE_PATH.put(img_path)
    if img_path=='' or None:
        return "Invalid Path"
        
    #image_label=classification_pred.main(img_path)
    #if not image_label:
    #    return "Invalid path"
    bucket=img_path.replace("gs://","").split("/")[0]
    folder=img_path.replace("gs://","").split("/",1)[-1]
  
    #path to images to be classified
    images_path=classification_pred.list_blobs(bucket,folder)
    print len(images_path)
    
    if images_path=="Invalid Bucket":
        return "Invalid bucket"
    #check if path exists
    if not images_path:
        #current_task.update_state(state='PROGRESS',
        #    meta={'stage': 'Path doesnot exist'})
        return "Invalid path"
    
    #Downloading fles to local
    #current_task.update_state(state='PROGRESS',
    #        meta={'stage': 'Downloading files from gcs'})
    images_path=classification_pred.download_blob(bucket,images_path)
    #print images_path
    logger.info("\nFiles Downloaded")
    #image_dictionary gives key as path to image and value as its array
    image_dictionary={}
    #current_task.update_state(state='PROGRESS',
    #        meta={'stage':'converting images into desired format'})
    for image in images_path:
        image_dictionary[image] = classification_pred._path_to_img(image)
    logger.info("\nImages converted into desired format")    

    #TODO
    #need to write a function which automatically used latest model from the model_directory
    #path to saved model
    export_dir = STAGING_AREA+"/"+CLASSIFICATION_MODEL_DIR 
    #current_task.update_state(state='PROGRESS',
    #        meta={'stage':'predicting classes'})
    #make_predictions
    output=classification_pred.prediction(export_dir,image_dictionary) 
    #print (output)
    #image_label gives path to image with its label
    #print output
    image_label={key:(CLASSIFICATION_LABEL_NOT_USEFUL if value < 0 else CLASSIFICATION_LABEL_USEFUL) for key,value in                  zip(image_dictionary.keys(), output) } 
    #current_task.update_state(state='PROGRESS',
    #        meta={'stage': 'Classification prediction completed'})

    logger.info("\nClassification prediction pipeline completed")
    #print (image_label)
    image_path=[]
    for key,value in image_label.items():    # for name, age in dictionary.iteritems():  (for Python 2.x)
        if value == CLASSIFICATION_LABEL_USEFUL:
            image_path.append(key)
            
    #subtask('object_detection', args=(image_path) )   
    if not image_path:
        #res=move.delay(image_path)
	res = move(image_path)
    else:    
        #res=object_detection.delay(image_path)  
	res=object_detection(image_path) 
    #task_id = res.task_id
    #TASK_ID.append(task_id)
    #res.update()
    
    #print ("job done")
    #image_label=classification_pred.main(img_path) 
    return "Job done..."

#@task
def object_detection(*args):
    print "object detection prediction started"
    img_path=IMAGE_PATH.get()
    IMAGE_PATH.put(img_path)
    print ("images_dir", img_path)
    print args[0]
    
    #Finding EOB Type
    EOBType = eob_type.get_eob_type('data/'+img_path.split('/', 3)[-1])
    
    #current_task.update_state(state='PROGRESS',
    #        meta={'stage': 'Object detection prediction started'})
    
    category_index,bb_info=object_detection_pred.main(args[0],img_path)
    
    #current_task.update_state(state='PROGRESS',
    #        meta={'stage': 'Object detection prediction completed'})
    print "object detection prediction completed"
    """res=ocr.delay(bb_info,category_index)  
    task_id = res.task_id
    res.update()"""
    print bb_info
    ocr(bb_info,category_index, EOBType)
   
    pass


@shared_task
def ocr(*args):
    """
    Perform OCR and push to DataStore
    """
    print "ocr started"
    """current_task.update_state(state='PROGRESS',
            meta={'stage': 'OCR started'})"""
    ocr_data,bb_info_data=ocr_eob.main(args[0],args[1])
    
    for data_ in ocr_data:
        data_['EOBType'] = args[2]
    print ("ocr data", ocr_data)    
    print "ocr ended"
    bb_info=args[0]
    category_index=args[1]
    #res=move.delay(ocr_data,category_index)  
    #task_id = res.task_id
    #TASK_ID.append(task_id)
    move(ocr_data,bb_info_data)
    #res.update()
    #move()
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
    img_path=IMAGE_PATH.get()
    IMAGE_PATH.put(img_path)
    print img_path
    move_files.main("move",img_path)
    
    print "files moved to labelled folder"
    ocr_data=args[0]
    bb_info_data=args[1]
   
    #Pushing ocr data in datastore
    if ocr_data:
        for data in ocr_data:
            db.post(data)
            
    #Pushing bb_info to datastore   
    for data in bb_info_data:
        print data
        db2.push(data)
        

    delete()
    
    
def delete(*args):
    img_path=IMAGE_PATH.get()
    IMAGE_PATH.put(img_path)
    print "deleting files from unlabelled folder"
    move_files.main("delete",img_path)
    print "files deleted from unlabelled folder"
    last=IMAGE_PATH.get()
    #files_to_del = os.listdir('data/unlabelled')
    #for file_ in files_to_del:
     #   os.remove('data/unlabelled/'+file_)
    #subprocess.call('rm -r data/unlabelled/*', shell=True)
    print ('last', last)
    shutil.rmtree('data/'+img_path.split('/', 3)[-1])
    #os.mkdir('data/unlabelled')
    
@task
def get_task_status(task_id):
    print "task_id=",task_id
    # If you have a task_id, this is how you query that task 
    task = AsyncResult(task_id)
 
    status = task.status
    progress = 0
 
    if status == u'SUCCESS':
        progress = 100
    elif status == u'FAILURE':
        progress = 0
    elif status == 'PROGRESS':
        progress = task.info["stage"]
 
    return {'status': status, 'stage': progress} 
    
    

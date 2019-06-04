from pathlib import Path
import time, os
import codecs, json 
from services import classification_pred,object_detection_pred,ocr_eob,move_files,input_function,online_prediction
from services.image_classifier_eob.prediction_simulation import Simulation
from services.db_connector import DataStore
import shutil
from vars_ import *
#from multiprocessing import Queue
#import queue
import time

#logger = get_task_logger(__name__)
TASK_ID=[]
# Init Database
# Specify KIND = ocr
db = DataStore(kind='ocr')

# Specify KIND = img_name for pushing bounding box data in datastore
db2 = DataStore(kind='img_name')
#IMAGE_PATH is used to put and get path of input image as an argument for all the functions
#IMAGE_PATH = queue.Queue(maxsize=20)
#IMAGE_PATH=None 

#@shared_task
def predictions(*args):
    print ("Job started")
    #time.sleep(10)
    #absolute path of data to be predicted 
    img_path=args[0]
    #global IMAGE_PATH 
    IMAGE_PATH =img_path
    #Ensure that the queue is empty
    #while IMAGE_PATH.empty()==False:
    #    IMAGE_PATH.get()
        
    #IMAGE_PATH.put(img_path)
    print "1image_path",IMAGE_PATH
    if img_path=='' or None:
        return "Invalid Path"
        

    #for automatic predictions(from cron job), default bucket is testeob
    if img_path!='automatic':
        bucket=img_path.replace("gs://","").split("/")[0]
        folder=img_path.replace("gs://","").split("/",1)[-1]

        #path to images to be classified
        images_path=classification_pred.list_blobs(bucket,folder)
        print len(images_path)    

        if images_path=="Invalid Bucket":
            return "Invalid bucket"
        #check if path exists
        if not images_path:
            return "Invalid path"
    
        #Downloading fles to local
        #current_task.update_state(state='PROGRESS',
        #        meta={'stage': 'Downloading files from gcs'})
        images_path=classification_pred.download_blob(bucket,images_path)
        #print images_path
        #logger.info("\nFiles Downloaded")
        image_path = classification_pred.main(images_path)
         #subtask('object_detection', args=(image_path) )   
        if not image_path:
            #res=move.delay(image_path)
            print "all paths not useful"
            res = move(IMAGE_PATH,None,None,None)
        else:    
            #res=object_detection.delay(image_path)  
            input_image_data = input_function.main(image_path)
            image_data = online_prediction.main(input_image_data)    
            res=object_detection(IMAGE_PATH,image_data) 
    #if img_path is automatic
    else:
        #getting generator for data entities from Datastore for prediction
        generator=db2.retrieve()
        print "data fetched from datastore"
        g = generator
        try:
            count = 1
            while True:
                #batch = [g.next().key.id_or_name for e in range(BATCH_SIZE)]
                batch = [g.next().key.id_or_name for e in range(BATCH_SIZE) if 'status' not in g.next().keys()]
                print batch
                if len(batch)!=0 :
                    #IMAGE_PATH.put(img_path)
                    data = classification_pred.download_blob(BUCKET,batch)
                    image_path=[]
                    if len(data)!=0:
                        image_path = classification_pred.main(data)      
                        print "image_path",image_path
                        if not image_path:
                            #res=move.delay(image_path)
                            print "all paths not useful"
                            res = move(IMAGE_PATH,None,None,data)                  
                        else:   
                            input_image_data = input_function.main(image_path)
                            image_data = online_prediction.main(input_image_data)
                            res=object_detection(IMAGE_PATH,image_data) 
                   
                    else:
                        print "Path does not exists"
                count += 1
        except StopIteration:
                print "ALL_BATCH_ENDs"
    
    
    
    """#image_dictionary gives key as path to image and value as its array
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
            image_path.append(key)"""
            
   
    #task_id = res.task_id
    #TASK_ID.append(task_id)
    #res.update()
    
    #print ("job done")
    #image_label=classification_pred.main(img_path) 
    return "Job done..."

#@task
def object_detection(IMAGE_PATH,*args):
    print "object detection prediction started"
    #global IMAGE_PATH
    img_path=IMAGE_PATH
    #IMAGE_PATH.put(img_path)
    print ("images_dir", img_path)
    #print args[0]
    
    #Finding EOB Type
    #EOBType = eob_type.get_eob_type('data/'+img_path.split('/', 3)[-1])
    new_result=[]
    if img_path == "automatic":
        result=args[0]
        for i in result:
            i=str(i['image_path'])
            i=i.rsplit("/",1)[0]
            new_result.append(i)
    else:
        print "img_path",img_path
        result = list(Path('data/'+img_path.split('/', 3)[-1]).glob('**/*.jpg'))
        for i in result:
            i=str(i)
            i=i.rsplit("/",1)[0]
            new_result.append(i)
    #new_result.append(Path(PATH).glob('**/*.jpg').rsplit("/",1)[0])
    print "results",result
    
        
    folders=set(new_result)
    print folders
    EOB_TYPE={}
    for image in folders:
        print image
        s=Simulation(image) 
        class_=s.action()
        EOB_TYPE[image.replace("data/","").replace("unlabelled","labelled")]=class_
    print "eob_type,img",EOB_TYPE,IMAGE_PATH    
    
    
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
    ocr(IMAGE_PATH,bb_info,category_index,EOB_TYPE,args[0])
   
    pass


#@shared_task
def ocr(IMAGE_PATH,*args):
    """
    Perform OCR and push to DataStore
    """
    print "ocr started"
    """current_task.update_state(state='PROGRESS',
            meta={'stage': 'OCR started'})"""
    ocr_data,bb_info_data=ocr_eob.main(args[0],args[1])
    #global IMAGE_PATH
    #update eob type in the results of ocr
    for data_ in ocr_data:  
        filename=data_['Filename'].rsplit("/",1)[0]
        print "filename ,img",filename, IMAGE_PATH
        print args[2]
        print args[2][filename]
        data_['EOBType'] = args[2][filename]
    print ("ocr data", ocr_data)    
    print "ocr ended"
    bb_info=args[0]
    category_index=args[1]
    #res=move.delay(ocr_data,category_index)  
    #task_id = res.task_id
    #TASK_ID.append(task_id)
    move(IMAGE_PATH,ocr_data,bb_info_data,args[3])
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

#@shared_task
def move(IMAGE_PATH,*args):
    print "moving files to labelled"
    #global IMAGE_PATH
    img_path=IMAGE_PATH
    #IMAGE_PATH.put(img_path)
    print img_path
    print args[2]
    move_files.main("move",img_path,args[2])
    
    print "files moved to labelled folder"
    ocr_data=args[0]
    bb_info_data=args[1]
   
    #Pushing ocr data in datastore
    if ocr_data:
        for data in ocr_data:
            db.post(data)
            
    #Pushing bb_info to datastore   
    if bb_info_data:
        for data in bb_info_data:
            print data
            db2.push(data)
        

    delete(IMAGE_PATH,args[2])
    
    
def delete(IMAGE_PATH,*args):
    #global IMAGE_PATH
    img_path=IMAGE_PATH
    #IMAGE_PATH.put(img_path)
    print "img_path",IMAGE_PATH
    print "deleting files from unlabelled folder"
    move_files.main("delete",img_path,args[0])
    print "files deleted from unlabelled folder"
    #last = IMAGE_PATH.get()
    #files_to_del = os.listdir('data/unlabelled')
    #for file_ in files_to_del:
     #   os.remove('data/unlabelled/'+file_)
    #subprocess.call('rm -r data/unlabelled/*', shell=True)
    #if img_path == "automatic":
    print "img ,args",IMAGE_PATH ,args[0]
    if args[0]!=None:
        for image in args[0]:
            if isinstance(image,dict):
                print image
                image_path=image['image_path']
                input_=image['image_string_tensor']
                output_=image['predictions_path']

                if os.path.exists(input_):
                    os.remove(input_)

                if os.path.exists(output_):
                    os.remove(output_)  

                if os.path.exists(image_path.rsplit("/",1)[0]):
                    shutil.rmtree(image_path.rsplit("/",1)[0])

    """else:    
        shutil.rmtree('data/'+img_path.split('/', 3)[-1])
    if (os.path.exists("data/inputs")):    
        shutil.rmtree("data/inputs")"""
    """if (os.path.exists("data/outputs")):    
        shutil.rmtree("data/outputs")"""
    #os.mkdir('data/unlabelled')
    
#@task
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
    
    

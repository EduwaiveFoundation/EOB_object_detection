from google.cloud import storage
from vars_ import *
import re
#from controller.tasks import IMAGE_PATH

def list_blobs(bucket_name,prefix):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix)
    list_blob=[]
    for blob in blobs:
        list_blob.append(blob.name)
    print list_blob    
    return list_blob    
        
def copy_blob(bucket_name, blob_name, new_blob_name):
    """Copies a blob from one bucket to another with a new name."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    source_blob = bucket.blob(blob_name)
    
    new_blob = bucket.copy_blob(
        source_blob, bucket, new_blob_name)
    
def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()   
    
def main(func,IMAGE_PATH,image_list=None):
    #If IMAGE_PATH is automatic data is retrieved from datastore so default bucket is testeob and image_list is to be passes as     #an argument
    print IMAGE_PATH
    print image_list
    if IMAGE_PATH == "automatic":
        bucket="testeob"
    else: 
        #retrieve the bucket name from input_path
        bucket=IMAGE_PATH.replace("gs://","").split("/")[0]
        source_path=IMAGE_PATH.replace("gs://","").split("/",1)[-1]
        #list of images on which function is to be performed
        image_list=list_blobs(bucket,source_path)
    for image in image_list:
        #image is of type dictionary when IMAGE_PATH is automatic
        if isinstance(image,dict):
            image=image['image_path']
        #replace "data/" which is staging area with ""    
        image = image.replace("data/","")
        #print image
        #check if image is already in labelled folder
        if not image.startswith("labelled"):
            destination_path=image.replace("unlabelled","labelled")
            if(func=="move"):
                print image
                copy_blob(bucket, image , destination_path)
            if(func=="delete"):
                delete_blob(bucket,image)
                
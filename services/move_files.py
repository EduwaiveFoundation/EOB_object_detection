from google.cloud import storage
from vars_ import *
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
    
def main(func,IMAGE_PATH):
    bucket=IMAGE_PATH.replace("gs://","").split("/")[0]
    source_path=IMAGE_PATH.replace("gs://","").split("/",1)[-1]
    image_list=list_blobs(bucket,source_path)
    for image in image_list:
        destination_path=image.replace("unlabelled","labelled")
        if(func=="move"):
            print image
            print destination_path
            copy_blob(bucket, image , destination_path)
        if(func=="delete"):
            delete_blob(bucket,image)
                
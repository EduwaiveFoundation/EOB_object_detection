import subprocess
import os
import shutil
from google.cloud import storage
from trainer.training_scripts import xml_to_csv
from trainer.training_scripts import generate_tfrecord


def list_blobs(bucket_name,prefix):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except:
        return "bucket does not exists"

    blobs = bucket.list_blobs(prefix=prefix)
    list_blobs=[]
    for blob in blobs:
        if(blob.name.endswith(".xml") or blob.name.endswith(".jpg")):
            list_blobs.append(blob.name)
            
    return list_blobs 

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

def download_blob(bucket_name, list_files):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    if not os.path.exists('data'):
        os.mkdir("data")
    for file in list_files:
        blob = bucket.blob(file)
        destination_file="data/"+file.split("/")[-1]
        blob.download_to_filename(destination_file)
    
def main(project,data_dir):
    #PROJECT="ace-automated-clean-eobs"
    #YOUR_GCS_BUCKET="gs://sampleeob"
    PROJECT=project
    GCS_BUCKET=data_dir.replace("gs://","").split("/")[0]
    TRAIN_DATA=data_dir.replace("gs://","").split("/",1)[-1]
    job_list=subprocess.check_output("gcloud ml-engine jobs list",shell=True)
    print job_list
    job=job_list.split("\n")
    latest_job_status=job[1].split(" ")
    print latest_job_status
    if latest_job_status[2]=="RUNNING":
        return {"status":"EOB-201","message":"Already Running"}
   
    else:
        list_files=list_blobs(GCS_BUCKET,TRAIN_DATA)
        if list_files == "bucket does not exists" or len(list_files) == 0:
            return "Invalid input path"
        download_blob(GCS_BUCKET,list_files)
        xml_to_csv.main()
        output_path="data/train.record"
        image_dir="data/"
        csv_input="data/train_labels.csv"
        generate_tfrecord.main(output_path,image_dir,csv_input)
        upload_blob(GCS_BUCKET,output_path,"data/train.record")

        os.chdir("/home/navneet/models/research")
        #subprocess.call("cd models/research",shell=True)
        subprocess.call("python setup.py sdist",shell=True)
        subprocess.call("(cd slim && python setup.py sdist)",shell=True)
        subprocess.call("gcloud config set project {}".format(PROJECT),shell=True)
        subprocess.call("gcloud ml-engine jobs submit training `whoami`_object_detection_`date +%s` \
        --job-dir=gs://{}/train \
        --packages dist/object_detection-0.1.tar.gz,slim/dist/slim-0.1.tar.gz \
        --module-name object_detection.train \
        --region=us-central1 \
        --runtime-version=1.12\
        -- \
        --train_dir=gs://sampleeob/data/ \
        --pipeline_config_path=gs://sampleeob/data/faster_rcnn_inception_v2_pets.config".format(GCS_BUCKET),shell=True)
        
        os.chdir("/home/navneet/Training API")
        shutil.rmtree('data')
        job_list=subprocess.check_output("gcloud ml-engine jobs list",shell=True)
        print job_list
        job=job_list.split("\n")
        job_status=job[1].split(" ")
        print job_status
        if job_status[0]!=latest_job_status[0]:
            status=job_status[2]
            if status!="FAILED" or status!="CANCELLED" or status!="RUNNING":
                return {"status":"EOB-200","message":status}
            elif status=="RUNNING":
                return {"status":"EOB-200","message":"Started Successfully"} 
            else:
                return {"status":"EOB-401","message":"Error Occured1"}
                
            
        else:
            return {"status":"EOB-401","message":"Error Occured2"}
              
        

    
if __name__ == "__main__": 
    print "Job started"
    PROJECT="ace-automated-clean-eobs"
    YOUR_GCS_BUCKET="gs://sampleeob"
    main(PROJECT,BUCKET)
else: 
    print "Executed when imported"

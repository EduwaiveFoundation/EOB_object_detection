from oauth2client.client import GoogleCredentials
from googleapiclient import discovery
from googleapiclient import errors
from frozen_graph_exporter import helper,helper1 
from google.cloud import storage
import os,subprocess,shutil
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
        list_blobs.append(blob.name)
            
    return list_blobs 

def download_blob(bucket_name, list_files):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    if not os.path.exists('trainer/training_scripts/data'):
        os.mkdir("trainer/training_scripts/data")
    if not os.path.exists('trainer/training_scripts/data/training'):
        os.mkdir("trainer/training_scripts/data/training")    
        
    for file in list_files:
        #file.split("/")[-1] gives name of file
        if(file.split("/")[-1])!="":
            blob = bucket.blob(file)
            destination_file="trainer/training_scripts/data/training/"+file.split("/")[-1]
            #print "blob",file
            #print "destination_foile",destination_file
            blob.download_to_filename(destination_file)
        

def main(project_id):
    ml = discovery.build('ml','v1')
    #initialise project for listing jobs
    project = 'projects/{}'.format(project_id)
    #request for listing jobs for given project
    request=ml.projects().jobs().list(parent=project)
    #executing the request
    response=request.execute()
    
    jobs_to_be_cancelled=[]
    
    #fetching the job_ids of all running jobs from response
    for job in response['jobs']:
        if job['state']=="RUNNING":
            print job['jobId']
            jobs_to_be_cancelled.append(job['jobId'])
            
    if len(jobs_to_be_cancelled)==0:
        return "No running jobs"
    
    status={}    
    #cancelling the jobs
    for job_id in jobs_to_be_cancelled:
        job = 'jobs/{}'.format(job_id)
        request = ml.projects().jobs().cancel(name="{}/{}".format(project,job))
        response = request.execute()
        if bool(response)==False:
            status[job_id]="successfully cancelled"
        else:
            status[job_id]=response
            
    #download the latest model checkpoints from gcs for object detection module
    list_=list_blobs("testeob","data")
    print list_
    download_blob("testeob",list_)
    #calling the exporter script to build and update the frozen inference graph in prediction pipeline
    helper.main("image_tensor")
        
    #call exporter function for input type=image_tensor
    os.chdir("/home/navneet/Training API/trainer/training_scripts/frozen_graph_exporter/models/research/")
    subprocess.call("export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim",shell=True)
    os.chdir("/home/navneet/Training API/trainer/training_scripts/frozen_graph_exporter/models/research/object_detection")
    #get latest model.ckpt file
    path="/home/navneet/Training API/trainer/training_scripts/data/training"
    res=[i for i in os.listdir(path) if i.startswith("model.ckpt-")]
    res.sort
    latest_model_file=res[0].rsplit(".",1)[0]
    output_directory="/home/navneet/Training API/trainer/training_scripts/data/frozen_inference_graph"
    if os.path.isdir(output_directory):
        shutil.rmtree(output_directory)
    subprocess.call("python export_inference_graph.py \
    --input_type encoded_image_string_tensor \
    --pipeline_config_path /home/navneet/Training\ API/trainer/training_scripts/data/pipeline.config \
    --trained_checkpoint_prefix /home/navneet/Training\ API/trainer/training_scripts/data/training/{}  \
    --output_directory /home/navneet/Training\ API/trainer/training_scripts/data/frozen_inference_graph".format(latest_model_file),shell=True)
    
    os.chdir("/home/navneet/Training API")
    shutil.copyfile("trainer/training_scripts/data/frozen_inference_graph/frozen_inference_graph.pb",                                   "/home/navneet/Classification1/pipeline/data/frozen_inference_graph.pb")

    
    #listing the previous version of model
    MODEL_NAME='eob_object_detection'
    model = 'models/{}'.format(MODEL_NAME)
    request=ml.projects().models().versions().list(parent="{}/{}".format(project,model))
    response =request.execute()
    #print response
    #i=len(response['versions'])
    version_to_be_deleted=''
    new_default_version=''
    if bool(response):
        for version in response['versions']:
            if 'isDefault' in version.keys():
                #delete version
                version_to_be_deleted="versions/{}".format(version['name'].split("/")[-1])

            else:
                version="versions/{}".format(version['name'].split("/")[-1])
                #set the non default version to default
                request = ml.projects().models().versions().setDefault(name="{}/{}/{}".format(project,model,version))
                request.execute()
                new_default_version=version

        #delete the previous default version
        version=version_to_be_deleted
        request = ml.projects().models().versions().delete(name="{}/{}/{}".format(project,model,version))
        request.execute()
        #version name for new version
        VERSION=[i for i in ["v1","v2","v3"] if i not in (version_to_be_deleted.split("/")[-1],new_default_version.split("/")[-1])]
        VERSION=VERSION[0]
        
    else:
        VERSION="v1"
      
    print "VERSION",VERSION
    version="versions/{}".format(VERSION)
    version_instances={
  "name": VERSION,
  "runtimeVersion": "1.13",
  "framework": "TENSORFLOW",
  "deploymentUri": "gs://testeob/model_directory/saved_model/"
}

    request = ml.projects().models().versions().create(parent="{}/{}".format(project,model),body=version_instances)
    response = request.execute()
    print response
    
    
    return "status"
    
    
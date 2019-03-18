"""import loggingfor handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)"""
import logging
logging.basicConfig(level=logging.DEBUG,filename='log.txt', filemode='a', \
                            format='%(levelname)s, %(message)s')
import os
import time
import tempfile
import shutil
#import pdf_to_image.convert.config as c
import multiprocessing
from itertools import product
from multiprocessing import Pool
from pdf2image import convert_from_path
from google.cloud import storage
import apche_beam_strategy as apache 

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

def list_blobs(bucket_name,pdf_file_path):
    pdf_list=[]
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix="{}".format(pdf_file_path))
    for blob in blobs:
        #path="{}/{}".format(bucket_name,blob.name)
        if(blob.name.endswith(".pdf")):
            pdf_list.append(blob.name)
        #print path
    return pdf_list
        
def input_location_type(input_path):
    if input_path.startswith("gs://"):
        input_type="gcs"
        input_bucket=input_path.replace("gs://","").split("/",1)[0]
        pdf_file_path=input_path.replace("gs://","").split("/",1)[-1]
    elif input_path.startswith("s3://"):
        input_type="s3"
        input_bucket=input_path.replace("s3://","").split("/",1)[0]
        pdf_file_path=input_path.replace("s3://","").split("/",1)[-1]
    else:
        input_type="local"
        input_bucket=None
        pdf_file_path=input_path
    return input_type,input_bucket,pdf_file_path

def output_location_type(output_path):
    if output_path.startswith("gs://"):
        output_type="gcs"
        output_bucket=output_path.replace("gs://","").split("/",1)[0]
        images_folder_path=output_path.replace("gs://","").split("/",1)[-1]
    elif output_path.startswith("s3://"):
        output_type="s3"
        output_bucket=output_path.replace("s3://","").split("/",1)[0]
        images_folder_path=output_path.replace("s3://","").split("/",1)[-1]
    else:
        output_type="local"
        output_bucket=None
        images_folder_path=output_path
    return output_type,output_bucket,images_folder_path




def main(input_path,output_path):
    print 1
    logging.info("main started")
    #global bucket1
    #global timestamp
    #global file1
    #dest_folder is location in bucket where all the jpegs will be stored
    #global dest_folder
    #global rootdir 
    global error 
    error="no error"
    t=time.localtime()
    timestamp = time.strftime('%b-%d-%y_%H:%M:%S', t)
    try:
        input_type,input_bucket,pdf_file_path=input_location_type(input_path)
        output_type,output_bucket,images_folder_path=output_location_type(output_path)
        print input_type
        print input_bucket
        print pdf_file_path
        print output_type
        print output_bucket
        print images_folder_path
        if input_type!="local":
            input_dir = tempfile.mkdtemp()
            if output_type!="local":
                output_dir=tempfile.mkdtemp()
                print input_dir
                if input_type=="gcs" and output_type=="gcs":
                    pdf_list=list_blobs(input_bucket,pdf_file_path)
                    apache.gcs_pipeline(input_bucket,pdf_file_path,pdf_list,input_dir,
                                               output_bucket,images_folder_path,output_dir)
            shutil.rmtree(input_dir)  
            shutil.rmtree(output_dir)
                
            """ if output_type!="local":
            output_dir=tempfile.mkdtemp()
            print output_dir
            if output_type=="gcs":
                apache.gcs_output_pipeline(output_bucket,images_folder_path,output_dir)
            shutil.rmtree(output_dir)"""
            
        
                
                
            
        #In local we dirpath = tempfile.mkdtemp()will create a folder named as bucket name to copy all the content of given folder from bucket
        """ if os.path.exists("{}".format(bucket1)):
            shutil.rmtree("{}".format(bucket1))
        os.mkdir("{}".format(bucket1))
        #In the local folder named as bucket,we will create another folder in which all pdf's will be stored
        #Bucket_Nmae->File_Name->PDF's
        os.mkdir("{}/{}".format(bucket1,file1))
        #This function will download contents of file(folder given as argument) to local directory made above
        pdf_path=[]
        list_blobs(bucket1,file1,pdf_path)
        dest_path="sampleeob/unlabelled"
        os.mkdir(dest_path)
        apache.func(pdf_path,dest_path)"""

        
        
    except Exception as err:
            logging.error("{},{}".format(timestamp,err))
            error=err
            
    finally: 
        return error         
            
     
    """finally:
        #Remove all the directories created in local machine before exiting
        if os.path.exists(dest_path):                
            shutil.rmtree(dest_path)    
        if os.path.exists(bucket1):    
            shutil.rmtree(bucket1)"""
       

        
if __name__== "__main__":
    main(input_path,output_path) 
    

import apache_beam as beam
import os
import time
import tempfile
import shutil
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from pdf2image import convert_from_path
from google.cloud import storage
import logging
logging.basicConfig(level=logging.DEBUG,filename='log.txt', filemode='a', \
                            format='%(levelname)s, %(message)s')
"""options = PipelineOptions()
options.view_as(StandardOptions).runner = 'DirectRunner'
p = beam.Pipeline(options=options)"""

"""def list_blobs(bucket_name,file1,pdf_path):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix="{}".format(file1))
    for blob in blobs:
        path="{}/{}".format(bucket_name,blob.name)
        pdf_path.append(path)
        #print path
    return pdf_path"""  

storage_client = storage.Client()

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

class Download_PDF(beam.DoFn):    
    def process(self,source_blob,input_dir,input_bucket):
        """Downloads a blob from the bucket."""
        #storage_client = storage.Client()
        #bucket = storage_client.get_bucket(bucket_name)
        bucket = storage_client.get_bucket(input_bucket)
        blob = bucket.blob(source_blob)
        local_path="{}".format(input_dir)
        if source_blob.endswith(".pdf"):
            pdf_name=source_blob.split("/")[-1]
            local_path="{}/{}".format(input_dir,pdf_name)
            blob.download_to_filename(local_path)
            
        #print("{}/{}".format(bucket_name,blob.name))    
        return [local_path]
    
class Convert_PDF_to_JPG(beam.DoFn):
    def process(self,path,dest_path):
        #print path
        if path.endswith(".pdf"):
                        pages=convert_from_path(path,300) 
                        #bucket_name=path.split("/")[0]
                        #pdf_file gives name of pdf file
                        file_name=path.split("/")[-1]
                        pdf_file=file_name[:-4]
                        destination="{}/{}".format(dest_path,pdf_file)
                        #make a directory JPEGs->pdf_file to save images of all pages of the particular pdf file
                        if not os.path.exists(destination):
                            os.mkdir("{}/{}".format(dest_path,pdf_file))
                        for page in pages:
                            page.save("{}/{}-page{}.jpg".format(destination,pdf_file,pages.index(page)),"JPEG")
                            page_name="{}-page{}.jpg".format(pdf_file,pages.index(page))
                        files=os.listdir("{}".format(destination))
                        files=[destination+"/"+ f for f in files]
                        #print files
                        return files
                    
                    
class Upload_Images_to_Bucket(beam.DoFn):
    def process(self,path,dest_path,input_bucket):
        """Uploads a file to the bucket."""
        #bucket_name=path.split("/")[0]
        #print path
        bucket = storage_client.get_bucket(input_bucket)
        source_file_name=path
        destination_blob_name="{}/{}".format(dest_path,path.split("/",3)[-1])
        #storage_client = storage.Client()
        #bucket = storage_client.get_bucket(bucket_name)
        pdf_name=path.split("/",4)[-2]+".pdf"
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        return [pdf_name]
        
class Move_PDF_to_Processed(beam.DoFn):
    def process(self,pdf_name,input_bucket,pdf_folder,last_element):
        if pdf_name!=last_processed_pdf or last_element==True:
            print "last{}".format(last_processed_pdf)
            print "current {}".format(pdf_name)
            blob_name="{}/{}".format(pdf_folder,last_processed_pdf)
            new_blob_name="{}/{}".format("processed_pdfs",last_processed_pdf)
            bucket = storage_client.get_bucket(input_bucket)
            source_blob = bucket.blob(blob_name)
            new_blob = bucket.copy_blob(source_blob,bucket,new_blob_name)

            source_blob.delete()
            global last_processed_pdf
            last_processed_pdf=pdf_name
        
        
def gcs_pipeline(input_bucket,pdf_file_path,pdf_list,input_dir,output_bucket,images_folder_path,output_dir):
    try:
        print "success 1" 
        p=beam.Pipeline()
        file_paths = pdf_list |  beam.ParDo(Download_PDF(),input_dir,input_bucket) 
        images_path = file_paths | beam.ParDo(Convert_PDF_to_JPG(),output_dir)
        pdf_name=images_path | beam.ParDo(Upload_Images_to_Bucket(),images_folder_path,input_bucket)
        global last_processed_pdf
        last_processed_pdf=pdf_list[0].split("/")[-1]
        pdf_folder=pdf_list[0].rsplit("/",1)[0]
        pdf_name|beam.ParDo(Move_PDF_to_Processed(),input_bucket,pdf_folder,last_element=False)
        [last_processed_pdf]|beam.ParDo(Move_PDF_to_Processed(),input_bucket,pdf_folder,last_element=True)
        print "success 2"
        
    except Exception as err:
        print err
        logging.error(err)
    
"""def gcs_output_pipeline(output_bucket,images_folder_path,output_dir):
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(output_bucket)
        images_path = file_paths | beam.ParDo(Convert_PDF_to_JPG(),output_dir)
        images_path | beam.ParDo(Upload_Images_to_Bucket(),images_folder_path)
        
    except Exception as err:
         logging.error(err)
        """
    
    

"""def func(pdf_list,output_path): 
    storage_client = storage.Client()
    bucket = storage_client.get_bucket("sampleeob")
    p=beam.Pipeline()
    file_paths = pdf_path |  beam.ParDo(Download_PDF(),output_path) 
    images_path = file_paths | beam.ParDo(Convert_PDF_to_JPG(),output_path)
    images_path | beam.ParDo(Upload_Images_to_Bucket(),output_path)"""
    #return p 

"""if __name__== "__main__":
    input_path="gs://sampleeob/Anthem A"
    output_path="gs://sampleeob/unlabelled"
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
        output_dir=tempfile.mkdtemp()
        print input_dir
        print output_dir
        print input_type
        if input_type == "gcs":
            print "true"
            pdf_list=list_blobs(input_bucket,pdf_file_path)
            print pdf_list
            gcs_input_pipeline(input_bucket,pdf_file_path,pdf_list,input_dir,
                                       output_bucket,images_folder_path,output_dir)
            print "done"
        shutil.rmtree(input_dir)  
        shutil.rmtree(output_dir)"""


    
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
from HandlerFactory import HandlerFactory, GCSHandler
from PDFToJPG import PDFToJPG

input_path="gs://sampleeob/Beacon"
output_path="gs://sampleeob/unlabelled"

input_key=input_path.split("/")[0]
output_key=output_path.split("/")[0]

input_dict={"gs:":'GCSHandler',
            "s3:":'AWSHandler',
            "local":'LocalHandler'}

# Create a GCS Handler from Abstract Handler Factory
gs = HandlerFactory.create(input_dict[input_key])

# Set the input and output sources
gs.__input__ = input_path.split("/",2)[-1]
gs.__output__ = output_path.split("/",2)[-1]
output_dir=gs.__download_location__
# Creating an instance of PDFToJPG class
pdf_api = PDFToJPG()

# Using GCS Handler as a strategy to read, download and upload to-and-from GCS.
pdf_api.__strategy__ = gs


storage_client = storage.Client()
last_processed_pdf=None


class Download_PDF(beam.DoFn):    
    def process(self,source_blob):
        """Downloads a blob from the bucket."""
        
        local_path=pdf_api.download(source_blob)
         
        return [local_path]
    
class Convert_PDF_to_JPG(beam.DoFn):
    def process(self,path):
        
        images_location=pdf_api.process(path)
 
        return images_location
                    
                    
class Upload_Images_to_Bucket(beam.DoFn):
    def process(self,path):
        """Uploads a file to the bucket."""
        
        pdf_name=pdf_api.export(path)
  
        return [pdf_name]
        
class Move_PDF_to_Processed(beam.DoFn):
    def process(self,pdf_name,pdf_folder,last_element):
        if((last_processed_pdf!=pdf_name or last_element==True) and last_processed_pdf!=None):
            pdf_api.move(pdf_folder,last_processed_pdf)
        global last_processed_pdf    
        last_processed_pdf=pdf_name
            #last_processed_pdf= pdf_api.move(pdf_name,pdf_folder,last_processed_pdf,last_element)
       
            
        
        
def gcs_pipeline(input_bucket,pdf_file_path,output_bucket,images_folder_path):
    #try:
        #pdf_list = GCSHandler.read()
     
        pdf_list=pdf_api.read()
        print "success 1" 
        p=beam.Pipeline()
        file_paths = pdf_list |  beam.ParDo(Download_PDF()) 
        
        images_path = file_paths | beam.ParDo(Convert_PDF_to_JPG())
        
        pdf_name=images_path | beam.ParDo(Upload_Images_to_Bucket())
        
        #global last_processed_pdf
        #last_processed_pdf=pdf_list[0].split("/")[-1]
        pdf_folder=pdf_list[0].rsplit("/",1)[0]
        pdf_name|beam.ParDo(Move_PDF_to_Processed(),pdf_folder,last_element=False)
        [last_processed_pdf]|beam.ParDo(Move_PDF_to_Processed(),pdf_folder,last_element=True)
        print "success 2"
        
        """except Exception,err:
        print err
        print Exception
        logging.error(err)"""
        
if __name__== "__main__":
    gcs_pipeline("sampleeob","Beacon","sampleeob","unlabelled")         
    



    
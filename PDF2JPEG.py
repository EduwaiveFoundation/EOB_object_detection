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
#import apche_beam_strategy as apache 

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

from HandlerFactory import HandlerFactory, GCSHandler
from PDFToJPG import PDFToJPG

storage_client = storage.Client()
# Creating an instance of PDFToJPG class
pdf_api = PDFToJPG()



last_processed_pdf=None


class Download_PDF(beam.DoFn):    
    def process(self,source_blob,gs):
        """Downloads a blob from the bucket."""
        # Using GCS Handler as a strategy to read, download and upload to-and-from GCS.
        pdf_api.__strategy__ = gs
        local_path=pdf_api.download(source_blob)
         
        return [local_path]
    
class Convert_PDF_to_JPG(beam.DoFn):
    def process(self,path,gs):
        # Using GCS Handler as a strategy to read, download and upload to-and-from GCS.
        pdf_api.__strategy__ = gs
        images_location=pdf_api.process(path)
 
        return images_location
                    
                    
class Upload_Images_to_Bucket(beam.DoFn):
    def process(self,path,gs):
        """Uploads a file to the bucket."""
        # Using GCS Handler as a strategy to read, download and upload to-and-from GCS.
        pdf_api.__strategy__ = gs
        pdf_name=pdf_api.export(path)
  
        return [pdf_name]
        
class Move_PDF_to_Processed(beam.DoFn):
    def process(self,pdf_name,pdf_folder,gs,last_element):
        # Using GCS Handler as a strategy to read, download and upload to-and-from GCS.
        pdf_api.__strategy__ = gs
        #print pdf_name
        if((last_processed_pdf!=pdf_name or last_element==True) and last_processed_pdf!=None):
            pdf_api.move(pdf_folder,last_processed_pdf)
        global last_processed_pdf    
        last_processed_pdf=pdf_name


def main(input_path,output_path):
    print "started"
    logging.info("main started")
    global error 
    error="Null"
    t=time.localtime()
    timestamp = time.strftime('%b-%d-%y_%H:%M:%S', t)
    try:
        #input_path="gs://sampleeob/Beacon"
        #output_path="gs://sampleeob/unlabelled"
        if input_path=="":
            error="Input path not provided"
            return error
        if output_path=="":
            error="Output path not provided"
            return error
        
        input_key=input_path.split("/")[0]
        output_key=output_path.split("/")[0]
        
        input_dict={"gs:":'GCSHandler',
                    "s3:":'AWSHandler',
                    "local":'LocalHandler'}
        if input_key in input_dict.keys(): 
            # Create a GCS Handler from Abstract Handler Factory
            #global gs
            gs = HandlerFactory.create(input_dict[input_key])          
        else:
            error="Invalid input path"
            return error

        

        # Set the input and output sources
        gs.__input__ = input_path.split("/",2)[-1]
        gs.__output__ = output_path.split("/",2)[-1]
        
        
        output_dir=gs.__download_location__
        # Using GCS Handler as a strategy to read, download and upload to-and-from GCS.
        pdf_api.__strategy__ = gs
        #pdf_list = GCSHandler.read()
        pdf_list=pdf_api.read()
        
        if pdf_list=="Invalid Bucket":
            error="Invalid Bucket Name"
        elif len(pdf_list)==0:
            error="Incorrect Input Path"
        else:    
            #print pdf_list
            print "success 1" 
            p=beam.Pipeline()
            file_paths = pdf_list |  beam.ParDo(Download_PDF(),gs) 

            images_path = file_paths | beam.ParDo(Convert_PDF_to_JPG(),gs)

            pdf_name=images_path | beam.ParDo(Upload_Images_to_Bucket(),gs)

            #global last_processed_pdf
            #last_processed_pdf=pdf_list[0].split("/")[-1]
            pdf_folder=pdf_list[0].rsplit("/",1)[0]

            pdf_name|beam.ParDo(Move_PDF_to_Processed(),pdf_folder,gs,last_element=False)

            [last_processed_pdf]|beam.ParDo(Move_PDF_to_Processed(),pdf_folder,gs,last_element=True)
            global last_processed_pdf
            last_processed_pdf=None
        print "success 2"
    
    
    except Exception as err:
            print err
            logging.error("{},{}".format(timestamp,err))
            error=err
            
    finally: 
        return error         
            

       

        
if __name__== "__main__":
    main(input_path,output_path) 
    #main("gs://sampleeob/Anthem-BlueCross","gs://sampleeob/unlabelled")
    

"""import loggingfor handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)"""
import logging
logging.basicConfig(level=logging.DEBUG,filename='log.txt', filemode='a', \
                            format='%(levelname)s, %(message)s')
import os
import time
import shutil
import pdf_to_image.convert.config as c
import subprocess
import multiprocessing
from itertools import product
from multiprocessing import Pool
from pdf2image import convert_from_path
from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    
def rename_blob(bucket_name, blob_name, new_name):
    """Renames a blob."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    new_blob = bucket.rename_blob(blob, new_name)
    
def download_blob(bucket_name, source_blob_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    #list all the blobs from the given folder in the bucket
    blobs = bucket.list_blobs(prefix="{}".format(source_blob_name))
    for blob in blobs:
        #getting name of files from complete path of that file
        name=blob.name.split("/")[-1]
        if name.startswith("processed_"):
            logging.info("{} already processed".format(blob.name))
        elif name.endswith(".pdf"):
            blob.download_to_filename("{}/{}".format(bucket1,blob.name))


def convert(d):
    try:
        #path of pdf file
        pdf_dir= rootdir + "/" + d
        path="{}".format(pdf_dir)
        if d.endswith(".pdf"):
                        pages=convert_from_path(path,300) 
                        #pdf_file gives name of pdf file
                        pdf_file=d[:-4]
                        #make a directory JPEGs->pdf_file to save images of all pages of the particular pdf file
                        os.mkdir("%s/%s"%("JPEGs",pdf_file))
                        path="{}/{}".format("JPEGs",pdf_file)
                        for page in pages:
                            page.save("%s/%s-page%d.jpg"%(path,pdf_file,pages.index(page)),"JPEG")
                        files=os.listdir("{}".format(path))
                        for f in files:
                            #Function to upload all the images of pdf file in the bucket
                            upload_blob(bucket1,"{}/{}/{}".format("JPEGs",pdf_file,f), 
                                        "{}/{}/{}".format(dest_folder,pdf_file,f))
                        #subprocess.call("gsutil -m cp -r {} {}".format(path,destination), shell=True)
                        logging.info("{},{},converted".format(timestamp,pdf_dir))
                        path1="{}/{}".format(file1,d)
                        idx=path1.rfind("/")
                        #Adding processed keyword before pdf_file name 
                        path2=path1[:idx+1]+"processed_"+path1[idx+1:]
                        #Renaming function to change pdf_file name to processed_pdf_file name
                        rename_blob(bucket1,"{}/{}".format(file1,d),"{}".format(path2))
                       
    except Exception as err:
        logging.error("{},{},{}".format(timestamp,d,err))
    
def main(bucket2,file2):
    logging.info("main started")
    global bucket1
    global timestamp
    global file1
    #dest_folder is location in bucket where all the jpegs will be stored
    global dest_folder
    global rootdir 
    dest_folder="unlabelled"
    bucket1=bucket2
    file1=file2
    rootdir = "{}/{}".format(bucket1,file1)
    t=time.localtime()
    timestamp = time.strftime('%b-%d_%H:%M', t)
    try:
        #In local we will create a folder named as bucket name to copy all the content of given folder from bucket
        if os.path.exists("{}".format(bucket1)):
            shutil.rmtree("{}".format(bucket1))
        os.mkdir("{}".format(bucket1))
        #In the local folder named as bucket,we will create another folder in which all pdf's will be stored
        #Bucket_Nmae->File_Name->PDF's
        os.mkdir("{}/{}".format(bucket1,file1))
        #This function will download contents of file(folder given as argument) to local directory made above
        download_blob(bucket1,file1)
        #subprocess.call("gsutil -m cp -r {} {}/".format(source,bucket2), shell=True)

        if os.path.exists("JPEGs"):
            shutil.rmtree('JPEGs')
        #this directory will save all the images converted from pdf's    
        os.mkdir("JPEGs")
 
        d=os.listdir(rootdir)
        p = Pool(5)
        #Multithreaded function to call conversion fuction given pdf file as argument to the function
        p.map(convert,d)
    except Exception as err:
            logging.error("{},{},{}".format(timestamp,file1,err))
     
    finally:
        #Remove all the directories created in local machine before exiting
        if os.path.exists("JPEGs"):                
            shutil.rmtree('JPEGs')    
        if os.path.exists(bucket1):    
            shutil.rmtree(bucket1)
       

        
if __name__== "__main__":
    main(bucket,file1)    
#print("yes")
"""import loggingfor handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)"""
import logging
logging.basicConfig(level=logging.DEBUG,filename='log.txt', filemode='a', \
                            format='%(levelname)s, %(message)s')
logging.info("started")
import os
import time
import shutil
import pdf_to_image.convert.config as c
import subprocess
import multiprocessing
from itertools import product
from multiprocessing import Pool
from pdf2image import convert_from_path



def convert(d):
    try:
        pdf_dir= rootdir + "/" + d
                    #os.mkdir("%s/%s"%("JPEGs",d))   
        path="{}".format(pdf_dir)
        #print("started7")
        if d.endswith(".pdf"):
                        #print("started")
                        pages=convert_from_path(path,300) 
                        pdf_file=d[:-4]
                        os.mkdir("%s/%s"%("JPEGs",pdf_file))
                        path="{}/{}".format("JPEGs",pdf_file)
                        for page in pages:
                            page.save("%s/%s-page%d.jpg"%(path,pdf_file,pages.index(page)),"JPEG")
                        path=path.replace(" ","\\ ")  
                        subprocess.call("gsutil -m cp -r {} {}".format(path,destination), shell=True)
                        logging.info("{},{},converted".format(timestamp,pdf_dir))
                        l=len(bucket1)
                        path1="{}/{}".format(rootdir,d)
                        path1=path1.replace(" ","\\ ")
                        path2=path1[l+1:]
                        idx=path2.rfind("/")
                        path2=path2[:idx+1]+"processed_"+path2[idx+1:]
                        new_path=path1[:l+1]+path2
                        subprocess.call("gsutil mv gs://{} gs://{}".format(path1,new_path), shell=True)
    except Exception as err:
        logging.info("{},{}".format(err,d))
    
def main(bucket,file1):
    logging.info("main started")
    try:
        global bucket1
        global timestamp
        t=time.localtime()
        timestamp = time.strftime('%b-%d_%H:%M', t)
        #print("started2")
        #bucket="sampleeob"
        #file1="Anthem-BlueCross"
        #dest_bucket="unlabelled"
        bucket1=bucket
        dest_bucket2=c.dest_bucket.replace(" ","\\ ")
        dest_local=bucket
        #print("nO")
        #bucket="sampleeob"
        bucket2=bucket.replace(" ","\\ ")
        #file1="Anthem"
        file2=file1.replace(" ","\\ ") 
        source="gs://{}/{}".format(bucket2,file2)
        global destination
        destination="gs://{}/{}".format(bucket2,dest_bucket2)
        #print("started3")
       
            #print("started4")
       
        #print("nav")
        if os.path.exists(dest_local):
            shutil.rmtree(dest_local)
        os.mkdir(dest_local)

        subprocess.call("gsutil -m cp -r {} {}/".format(source,bucket2), shell=True)

        global rootdir 
        rootdir = "{}/{}".format(dest_local,file1)
        if os.path.exists("JPEGs"):
            shutil.rmtree('JPEGs')
        os.mkdir("JPEGs")
        #print("neet")
        d=os.listdir(rootdir)
        p = Pool(5)
        p.map(convert,d)
    except Exception as err:
            logging.info(err)
            logging.info("ERROR")
            #print("started5")
    finally:        
        if os.path.exists("JPEGs"):                
            shutil.rmtree('JPEGs')
        dest_local=bucket    
        if os.path.exists(dest_local):    
            shutil.rmtree(dest_local)
        #logging.info("ERROR") 

        
if __name__== "__main__":
    main(bucket,file1)      

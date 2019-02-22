#import config
"""def __init__(self):
    bucket=config.bucket
    source=config.source
    print source
    print bucket """
import os    
bucket=raw_input("Bucket Name?")
dest_bucket=raw_input("destination folder?")
source="gs://{}".format(bucket)
dest_local="bucket/"
destination="gs://{}/{}/".format(bucket,dest_bucket)

os.mkdir(dest_local)

import subprocess
subprocess.call("gsutil -m cp -r {} {}".format(source,dest_local), shell=True)

import os
from pdf2image import convert_from_path
rootdir = "{}{}".format(dest_local,bucket)
os.mkdir("JPEGs")
for dir in os.listdir(rootdir):
            pdf_dir= rootdir + "/" + dir
            #os.getcwd()
           
            os.mkdir("%s/%s"%("JPEGs",dir))   
            print pdf_dir
            #os.chdir(pdf_dir)
            for pdf_file in os.listdir(pdf_dir):
                #print pdf_file
                path="{}/{}".format(pdf_dir,pdf_file)
                if pdf_file.endswith(".pdf"):
                    pages=convert_from_path(path,300) 
                    pdf_file=pdf_file[:-4]
                    #print(pdf_file)
                   
                   
                    os.mkdir("%s/%s/%s"%("JPEGs",dir,pdf_file))
                    path="{}/{}/{}".format("JPEGs",dir,pdf_file)
                    path2="{}/{}".format("JPEGs",dir)
                    for page in pages:
                        page.save("%s/%s-page%d.jpg"%(path,pdf_file,pages.index(page)),"JPEG")
                    path2=path2.replace(" ","\\ ")    
                    subprocess.call("gsutil -m cp -r {} {}".format(path2,destination), shell=True)


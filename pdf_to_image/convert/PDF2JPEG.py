def main(bucket,file):
    import os 
    import shutil
    import config
    import subprocess
    from pdf2image import convert_from_path
   
    source="gs://{}/{}".format(bucket,file)
    destination="gs://{}/{}".format(bucket,config.dest_bucket)
    os.mkdir(config.dest_local)
    #print "yes"


    
    subprocess.call("gsutil -m cp -r {} {}/".format(source,config.dest_local), shell=True)

   
   
    rootdir = "{}/{}".format(config.dest_local,file)
    os.mkdir("JPEGs")
    for d in os.listdir(rootdir):
                pdf_dir= rootdir + "/" + d
                #os.getcwd()

                os.mkdir("%s/%s"%("JPEGs",d))   
                #print pdf_dir
                #os.chdir(pdf_dir)
                #for pdf_file in os.listdir(pdf_dir):
                    #print pdf_file
                path="{}".format(pdf_dir)
                if d.endswith(".pdf"):
                    pages=convert_from_path(path,300) 
                    pdf_file=d[:-4]
                    #print(pdf_file)


                    os.mkdir("%s/%s"%("JPEGs",pdf_file))
                    path="{}/{}".format("JPEGs",pdf_file)
                    path2="{}/{}".format("JPEGs",d)
                    for page in pages:
                        page.save("%s/%s-page%d.jpg"%(path,pdf_file,pages.index(page)),"JPEG")
                    path=path.replace(" ","\\ ")  
                    #print path2
                    #print destination
                    subprocess.call("gsutil -m cp -r {} {}".format(path,destination), shell=True)
                    #print "done"
                    #shutil.rmtree(path)
                    #shutil.rmtree(path2)
    shutil.rmtree('JPEGs')
    shutil.rmtree(config.dest_local)




























"""
#import config
def main(bucket):
    import os    
    #source=raw_input("Bucket Name?")
    dest_bucket="JPEGs"
    source="gs://{}".format(bucket)
    dest_local="bucket/"
    destination="gs://{}/{}/".format("sampleeob",dest_bucket)

    os.mkdir(dest_local)

    import subprocess
    subprocess.call("gsutil -m cp -r {} {}".format(source,dest_local), shell=True)

    import os
    from pdf2image import convert_from_path
    rootdir = "{}".format(dest_local)
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
                        os.remove(path)
                        os.remove(path2)
    os.remove("JPEGs")
    os.remove(dest_local) """


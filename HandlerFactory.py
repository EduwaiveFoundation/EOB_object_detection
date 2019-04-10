import abc
import tempfile
import shutil
from google.cloud import storage
from pdf2image import convert_from_path
import os
storage_client = storage.Client()

class HandlerFactory(object):
    __metaclass__ = abc.ABCMeta
    """
    Factory to create Readers for pulling files to server
    Currently supports
    - GCSReader
    - AWSReader
    - FilesReader
    """
    
    @staticmethod
    def create(typ):
        return globals()[typ]()
    
    @abc.abstractproperty
    def __input__(self):
        pass
    
    @abc.abstractproperty
    def __output__(self):
        pass
    
    @abc.abstractmethod
    def read(self):
        """
        Define to read the list of files to be processed by the reader
        """
        pass
    
    @abc.abstractmethod
    def download(self):
        """
        Downloads files from the source
        """
        pass
    
    @abc.abstractmethod
    def process(self):
        pass
    
    @abc.abstractmethod
    def upload(self):
        """
        Uploads files to the source
        """
        pass


class GCSHandler(HandlerFactory):
    """
    Reader class for handling files from GCS 
    """
    def __init__(self):
        """
        Initialise input and output source
        """
        self.input = None
        self.output = None
        self.temp_file=tempfile.mkdtemp()
    
    @property
    def __input__(self):
        return self.input #= value(getter)
    
    @property
    def __output__(self):
        return self.output# = value(getter)
    
    @property
    def __download_location__(self):
        return self.temp_file
    
    @__input__.setter
    def __input__(self, value):
        self.input = value
        
    @__output__.setter
    def __output__(self, value):
        self.output = value
        
    def read(self, *args):
        
        """Implement Reading method  
        Argument=input path"""
        input_path=self.__input__
        bucket_name=input_path.split("/",1)[0]
        pdf_path=input_path.split("/",1)[-1]
        pdf_list=[]
        bucket=''
        try:
            bucket = storage_client.get_bucket(bucket_name)
        except:
            print "given bucket does not exists"
            return "Invalid Bucket"
        
        blobs = bucket.list_blobs(prefix="{}".format(pdf_path))
        for blob in blobs:
             if(blob.name.endswith(".pdf")):
                pdf_list.append(blob.name)
                    
        #Read from __input__
        #print pdf_list
        
         #Read from __input__
        print ("GCS read")
        return pdf_list
       
    
    def download(self, *args):
        """
        Implement download or pull files method
        """
        pdf_path=args[0]
        #print pdf_path
        pdf_name=pdf_path.split("/")[-1]
        #print pdf_name
        input_path=self.__input__
        #print input_path
        bucket_name=input_path.split("/",1)[0]
        #print bucket_name
        download_path=self.__download_location__
        print download_path
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(pdf_path)
        local_path="{}".format(download_path)
        #print local_path
        if pdf_path.endswith(".pdf"):
            local_path="{}/{}".format(download_path,pdf_name)
            blob.download_to_filename(local_path) 
            print "sucess"
        #print(self.__download_location__)
        #Download from __input__
        print ("GCS download")    
        return local_path
       
        
    def process(self,*args):
        pdf_path=args[0]
        images_destination=self.__download_location__
        if pdf_path.endswith(".pdf"):
                        pages=convert_from_path(pdf_path,300) 
                        file_name=pdf_path.split("/")[-1]
                        pdf_file=file_name[:-4]
                        destination="{}/{}".format(images_destination,pdf_file)
                        #make a directory JPEGs->pdf_file to save images of all pages of the particular pdf file
                        if not os.path.exists(destination):
                            os.mkdir("{}/{}".format(images_destination,pdf_file))
                        for page in pages:
                            page.save("{}/{}-page{}.jpg".format(destination,pdf_file,pages.index(page)),"JPEG")
                            page_name="{}-page{}.jpg".format(pdf_file,pages.index(page))
                        files=os.listdir("{}".format(destination))
                        files=[destination+"/"+ f for f in files]
                        #print files
                        print ("GCS process")
                        return files
        
      
    
    def upload(self, *args):
        #print 1
        image_path=args[0]
        print image_path
        output_path=self.__output__
        bucket_name=output_path.split("/",1)[0]
        output_path=output_path.split("/",1)[-1]
        
        bucket = storage_client.get_bucket(bucket_name)
        source_file_name=image_path
        destination_blob_name="{}/{}".format(output_path,image_path.split("/",3)[-1])
        #storage_client = storage.Client()
        #bucket = storage_client.get_bucket(bucket_name)
        pdf_name=image_path.split("/")[-2]+".pdf"
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        
        
        #remove tempfile
        print ("GCS upload")
        return pdf_name
    
    def move(self, *args):
        #pdf_name=args[0]
        input_path=self.__input__
        bucket_name=input_path.split("/",1)[0]
        pdf_folder=args[0]
        last_processed_pdf=args[1]
        #last_element=args[2]
        print "GCS move"
       # if pdf_name!=last_processed_pdf or last_element==True:
            #print "last{}".format(last_processed_pdf)
            #print "current {}".format(pdf_name)
        blob_name="{}/{}".format(pdf_folder,last_processed_pdf)
        new_blob_name="{}/{}".format("processed_pdfs",last_processed_pdf)
        bucket = storage_client.get_bucket(bucket_name)
        source_blob = bucket.blob(blob_name)
        new_blob = bucket.copy_blob(source_blob,bucket,new_blob_name)
        source_blob.delete()
            #last_processed_pdf=pdf_name 
        print("GCS moved to processed_pdfs")

        
        
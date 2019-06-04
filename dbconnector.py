#Datastore connector for Google Cloud 
# Imports the Google Cloud client library
from google.cloud import datastore
from google.cloud import storage
import os
import config

class DataStore:
    
    def __init__(self):
        """
        Initializing the namespace 
        """
        self.client = datastore.Client(namespace='eob_predictions_data')
        self.kind = 'ocr'
        self.key = self.client.key(self.kind)
        self.query = self.client.query(kind=self.kind)

        
    def download_blob(self,bucket_name, source_blob_name, destination_file_name):
        """Downloads a blob from the bucket."""
	print "Download started"
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        if blob.exists():
            blob.download_to_filename(destination_file_name)  
        
        
    def retrieve(self):
        #self.query.add_filter('EOBType','>','NULL')
        results = list(self.query.fetch(limit=1))
        label_map = []
        for data in results:
            if 'EOBType' in data.keys():
                label_map.append({"file":data.key.id_or_name,"label":data['EOBType']})
            
        for files in label_map:
            label=files['label']
            file_=files['file'].replace("%20"," ")
            print file_
            destination_file=os.path.join(os.getcwd(),config.train_dir,label,file_.split("/")[-1])
            print "destination:",destination_file
            if not os.path.isdir(os.path.join(os.getcwd(),config.train_dir, label)):
                os.mkdir(os.path.join(os.getcwd(),config.train_dir, label))
            self.download_blob(config.BUCKET_NAME,file_,destination_file)
            
         


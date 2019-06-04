#Datastore connector for Google Cloud 
# Imports the Google Cloud client library
from google.cloud import datastore
from google.cloud import storage
import os

class DataStore:
    
    def __init__(self):
        """
        Initializing the namespace 
        """
        self.client = datastore.Client(namespace='eob_datastore_final')
        self.kind = 'img_name'
        self.key = self.client.key(self.kind)
        self.query = self.client.query(kind=self.kind)        
        
    def retrieve(self):
        self.query.add_filter('status','=','SAVED')
        results = list(self.query.fetch())
        label_map = []
        for data in results:
            label_map.append(data.key.id_or_name)
        print label_map
        return label_map
    



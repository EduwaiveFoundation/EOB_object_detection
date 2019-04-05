# Datastore connector for Google Cloud 
# Imports the Google Cloud client library
from google.cloud import datastore

class DataStore:
    
    def __init__(self, kind):
        """
        Initializing the namespace
        """
        self.client = datastore.Client(namespace='eob_predictions_data')
        self.kind = kind
        
    def post(self, data):
        """
        Pushes or updates data into the datastore
        - Performs UPSERT
        """
        assert data['Filename']
        key = self.client.key(self.kind, data.pop('Filename'))
        task = datastore.Entity(key=key)
        
        task.update(data)
        
        self.client.put(task)
    

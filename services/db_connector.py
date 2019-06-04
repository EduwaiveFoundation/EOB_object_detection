# Datastore connector for Google Cloud 
# Imports the Google Cloud client library
from google.cloud import datastore

class DataStore:
    
    def __init__(self, kind):
        """
        Initializing the namespace 
        """
        # Instantiates a client
        self.client = datastore.Client(namespace='eob_predictions_data')
        self.client2 = datastore.Client(namespace='eob_datastore_final')
        self.kind = kind
        #Initialize query for retrieving entities of given kind 
        self.query = self.client2.query(kind=self.kind)
        
    def post(self, data):
        """
        Pushes or updates data into the datastore
        - Performs UPSERT
        """
        assert data['Filename']
        #The Cloud Datastore key for the new entity
        key = self.client.key(self.kind, data.pop('Filename'))
        # Prepares the new entity
        task = datastore.Entity(key=key)
        #update data stored in datastore
        task.update(data)
        
        self.client.put(task)
        
    def push(self,data):  
        """
        Pushes or updates data into the datastore
        - Performs UPSERT
        """
        assert data['key']
        key =self.client2.key(self.kind,data.pop('key'))
        task=datastore.Entity(key=key)
         
        task.update(data)
        
        self.client2.put(task)
        #update the status field in datastore
        if 'status' in task:
            del task['status']
            self.client2.put(task)
        
    def retrieve(self):
        results = self.query.fetch()
        print results 
        #generator object _page_iter
        pages = results.pages
        print pages
        #generator object for each row fetched 
        page = next(pages)
        print page
        #returns a generator of query fetched
        return page     


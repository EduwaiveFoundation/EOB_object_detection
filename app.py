#imports 
from __future__ import absolute_import
from prediction import Prediction
from train import Train
from model import Model
from flask import Flask
from flask_cors import CORS, cross_origin
from flask import jsonify,request
from dbconnector import DataStore
import fire, config 
import shutil
import os,glob
#import celery1
from celery import Celery

db=DataStore()
app = Flask(__name__)
cors = CORS(app)
"""app.config.update(
    CELERY_BROKER_URL='redis://some-redis:6379',
    CELERY_RESULT_BACKEND='redis://some-redis:6379'
)
celery = celery1.make_celery(app)
"""
# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

@celery.task
def action():
    print "In celery"
    training = Train(config.train_dir ,config.model_dir ,config.valid_dir)
    
    #retriving data fom datastore
    db.retrieve()
    if training.action()=="Invalid classes":
        print "Classes Missing"
    #else:
        #list_of_files = glob.glob(os.path.join(config.model_dir, "*.h5")) # * means all if need specific format then *.csv
        #latest_file = max(list_of_files, key=os.path.getctime)
    shutil.rmtree("/home/navneet/Classification1/pipeline/services/image_classifier_eob/model_dir")    
    shutil.copytree("model_dir","/home/navneet/Classification1/pipeline/services/image_classifier_eob/model_dir")    
    print "out celery"
    
    
@app.route('/eob_type_classification/',methods=['GET'])
@cross_origin(allow_headers=['Content-Type', 'Authorization'])
def eob_type_Classification():
    print config.train_dir
    print config.valid_dir
    print "celery_started"
    
    action.delay()
    print "celery stopped"
    return "trainig started"
    


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=int("6666")) 


    

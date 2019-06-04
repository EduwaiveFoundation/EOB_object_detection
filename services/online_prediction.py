from oauth2client.client import GoogleCredentials
from googleapiclient import discovery
from googleapiclient import errors
from vars_ import *
import os,time
import pwd,json

def main(input_image_path):
    #Building a Python representation of the API
    ml = discovery.build('ml','v1')
    #initialise project for listing jobs
    project = 'projects/{}'.format(PROJECT_ID)
    #initialise the model
    model = 'models/{}'.format(MODEL_NAME)
    #list versions of the model
    request=ml.projects().models().versions().list(parent="{}/{}".format(project,model))
    response =request.execute()
    i = len(response['versions'])
    #print len(response2['versions'])
    #initialise the latest version
    VERSION="v{}".format(i)
    version = "versions/{}".format(VERSION)
    i = 0
    for image in input_image_path:
        json_instances_file = image['image_string_tensor']
        print "prediction"
        print image['image_path']
        body={'instances':[]}
        with open (json_instances_file) as json_file:
            data = json.load(json_file)
            body['instances'].append(data)

        parent="{}/{}/{}".format(project,model,version)
        try:
            #request for online predictions
            response1 = ml.projects().predict(
                    name=parent,
                    body=body
                ).execute()           

        except Exception as e:
            print e
            input_image_path[i]['predictions_path'] = "size exceeds"
            return input_image_path
            
        image_name=image['image_path'].split("/")[-1].replace(".jpg",".txt")
        if not os.path.exists(OUTPUT_PATH.split("/")[0]):
            os.mkdir(OUTPUT_PATH.split("/")[0])
        if not os.path.exists(OUTPUT_PATH):
            os.mkdir(OUTPUT_PATH)
        #saving the response in local machine    
        with open ("{}/{}".format(OUTPUT_PATH,image_name),'w') as f:
            for prediction in response1['predictions']:
                f.write(json.dumps(prediction))
        #saving the path of output file in dictionary        
        input_image_path[i]['predictions_path'] = "{}/{}".format(OUTPUT_PATH,image_name )       
        i=i+1
    #returns the updated input_image_path containig path of output files
    return input_image_path  
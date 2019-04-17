import subprocess
def main(project):
    job_list=subprocess.check_output("gcloud ml-engine jobs list",shell=True)
    job=job_list.split("\n")
    latest_job_status=job[1].split(" ")
    print latest_job_status
    status=latest_job_status[2]
    if status=="RUNNING" or status=="PREPARING" or status=="SUCCEEDED":
        return {"status":"EOB-201","message":status}
    elif status=="CANCELLED" or status=="FAILED":
        return {"status":"EOB-401","message":status}
    else:
        return {"status":"EOB-401","message":status}
        
   
    """outputs=subprocess.check_output("gcloud ml-engine jobs describe {}".format(job),shell=True)
    print "output=",outputs
    outputs=outputs.split("\n")
    output_dictionary={}
    for output in outputs:
        output=output.split(":")
        #print output
        key=output[0]
        if(len(output)>1):
            value=output[1]
        else:
            value=None
        output_dictionary[key]=value
        
    print output_dictionary['state']  """   
    

"""from oauth2client.client import GoogleCredentials
from googleappiclient import discovery
from googleapiclient import errors

def main(project_name,job_name):
    ml = discovery.build('ml','v1')

    #projectName = 'ACE - Automated Clean EOBs'
    projectName=project_name
    projectId = 'projects/{}'.format(projectName)
    jobName=job_name
    #jobName = 'navneet_object_detection_1555323427'
    jobId = '{}/jobs/{}'.format(projectId, jobName)

    request = ml.projects().jobs().get(name=jobId)

    response = None

    try:
        response = request.execute()
    except errors.HttpError, err:
        print (err)
        # Something went wrong. Handle the exception in an appropriate
        #  way for your application.

    if response == None:
        print("none")
        # Treat this condition as an error as best suits your
        # application.
    else:    
        print('Job status for {}.{}:'.format(projectName, jobName))
        print('    state : {}'.format(response['state']))
        print('    consumedMLUnits : {}'.format(
            response['trainingOutput']['consumedMLUnits'])) """  

if __name__ == "__main__": 
    print "started"
    PROJECT='ace-automated-clean-eobs'
    jobName = 'navneet_object_detection_1555332461'
    main(PROJECT,jobName)
else: 
    print "Executed when imported"
        
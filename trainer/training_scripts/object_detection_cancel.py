from oauth2client.client import GoogleCredentials
from googleapiclient import discovery
from googleapiclient import errors

def main(project_id):
    ml = discovery.build('ml','v1')
    #initialise project for listing jobs
    project = 'projects/{}'.format(project_id)
    #request for listing jobs for given project
    request=ml.projects().jobs().list(parent=project)
    #executing the request
    response=request.execute()
    
    jobs_to_be_cancelled=[]
    
    #fetching the job_ids of all running jobs from response
    for job in response['jobs']:
        if job['state']=="RUNNING":
            print job['jobId']
            jobs_to_be_cancelled.append(job['jobId'])
            
    if len(jobs_to_be_cancelled)==0:
        return "No running jobs"
     
    status={}    
    #cancelling the jobs
    for job_id in jobs_to_be_cancelled:
        project = 'projects/{}/jobs/{}'.format(project_id,job_id)
        request = ml.projects().jobs().cancel(name=project)
        response = request.execute()
        if bool(response)==False:
            status[job_id]="successfully cancelled"
        else:
            status[job_id]=response
        
    return status
    
    
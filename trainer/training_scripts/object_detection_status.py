import subprocess
def main(project):
    job_list=subprocess.check_output("gcloud ml-engine jobs list",shell=True)
    job=job_list.split("\n")
    latest_job_status=job[1].split(" ")
    print latest_job_status
    #latest_job_status[2] gives status of job
    status=latest_job_status[2]
    if status=="RUNNING" or status=="PREPARING" or status=="SUCCEEDED":
        return {"status":"EOB-201","message":status}
    elif status=="CANCELLED" or status=="FAILED":
        return {"status":"EOB-401","message":status}
    else:
        return {"status":"EOB-401","message":status}
        
if __name__ == "__main__": 
    print "started"
    PROJECT='ace-automated-clean-eobs'
    jobName = 'navneet_object_detection_1555332461'
    main(PROJECT,jobName)
else: 
    print "Executed when imported"
        
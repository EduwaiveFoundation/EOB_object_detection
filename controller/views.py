# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from rest_framework.renderers import JSONRenderer
#from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .tasks import predictions,object_detection,ocr,move_files,get_task_status,TASK_ID

# Create your views here.
#TASK_ID = None

def training(request):
    """
    Job API to submit training job
    """
    response = {
        "status": "OK",
        "err": None
    }
    return JsonResponse(response)


class List(APIView):
    renderer_classes = (JSONRenderer, )
    def post(self, request):

        """
        Job API to submit prediction job
        """
        global TASK_ID
        img_path=request.data['input_path']
        #task=predictions.delay(img_path)
        task=predictions(img_path)
        #TASK_ID.insert(0,task.id)    

        response = {
            "status": "OK",
            "err": None
        }
        return JsonResponse(response)
    
def status(request):
    """
    GET status of the current jobs
    """
    global TASK_ID
    response = {}
    if TASK_ID == None:
        return JsonResponse({"status": "No Jobs running"})
    for task in TASK_ID:
        response[task] = get_task_status(task)
    #json_data = serializers.serialize('json', [json_list,])
    #struct = json.loads(json_data)
    #data = json.dumps(struct[0])
    return JsonResponse(response, content_type='json')   
    #return json_list    

    """response = {
        "status": "OK",
        "err": None
    }
    return JsonResponse(response)"""

def error(request):
    """
    Error page
    """
    response = {
        "status": 404,
        "err": "Page doesnt exists"
    }
    return JsonResponse(response)

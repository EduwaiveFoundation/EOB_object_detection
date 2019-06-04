# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
import object_detection_trainer,object_detection_status,object_detection_cancel
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer


import os,glob

class Train(APIView):
    renderer_classes = (JSONRenderer, )
    def post(self,request):
        client_name=request.data['client_name']
        if(client_name!="eob"):
            response={"status":"EOB-401","message":"Invalid client name"}
        else:  
            project_id="ace-automated-clean-eobs"
            #bucket="gs://sampleeob"
            response=object_detection_trainer.main(project_id)
            print response  
            
        return Response((response), status=200)
    

class Status(APIView):
    renderer_classes = (JSONRenderer, )
    def post(self,request):
        client_name=request.data['client_name']
        if(client_name!="eob"):
            response={"status":"EOB-401","message":"Invalid client name"}
        else: 
            project_id="ace-automated-clean-eobs"
            response=object_detection_status.main(project_id)
             
        return Response((response), status=200)
    
class Cancel(APIView):
    renderer_classes = (JSONRenderer, )
    def post(self,request):
        client_name=request.data['client_name']
        if(client_name!="eob"):
            response={"status":"EOB-401","message":"Invalid client name"}
        else: 
            project_id="ace-automated-clean-eobs"
            response=object_detection_cancel.main(project_id)
        
        return Response((response), status=200)
        
    
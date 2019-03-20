# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
import pdf_to_image.convert.PDF2JPEG as pd
from django.http import HttpResponse
from rest_framework import status
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
import os,glob

def get_var_value(filename="job_id.txt"):
        with open(filename, "a+") as f:
            f.seek(0)
            val = int(f.read() or 0) + 1
            f.seek(0)
            f.truncate()
            f.write(str(val))
            return val

class pdfList(APIView):
    renderer_classes = (JSONRenderer, )
    def post(self,request):
        job_id_counter = get_var_value()
        error_info=pd.main(request.data['bucket'],request.data['file'])
        try:
            json_response={"status":"OK","job_id":job_id_counter,"error_info":error_info}
        except exception as err:
            json_response={"status":"ERROR", "job_id":job_id_counter,"error_info":error_info}
            
        return Response((json_response),status=200)

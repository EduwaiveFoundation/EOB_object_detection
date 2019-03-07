# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
import PDF2JPEG
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer

import os,glob

class pdfList(APIView):
    renderer_classes = (JSONRenderer, )
    def post(self,request):
        PDF2JPEG.main(request.data['bucket'],request.data['file'])
        try:
            x={"status":"completed"}
        except:
            x={"status":"error"}
            
        return Response((x), status=200)

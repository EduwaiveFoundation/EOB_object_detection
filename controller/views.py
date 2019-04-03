# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from django.shortcuts import render
from .tasks import predictions

# Create your views here.
def training(request):
    """
    Job API to submit training job
    """
    response = {
        "status": "OK",
        "err": None
    }
    return JsonResponse(response)

def prediction(request):
    """
    Job API to submit prediction job
    """
    predictions.delay()
    response = {
        "status": "OK",
        "err": None
    }
    return JsonResponse(response)

def status(request):
    """
    GET status of the current jobs
    """
    response = {
        "status": "OK",
        "err": None
    }
    return JsonResponse(response)

def error(request):
    """
    Error page
    """
    response = {
        "status": 404,
        "err": "Page doesnt exists"
    }
    return JsonResponse(response)

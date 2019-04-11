# OCR API

#imports 
import os
import io
import time
from google.cloud import vision
from PIL import Image
from matplotlib import pyplot as plt
from vars_ import *

#from controller.tasks import IMAGE_PATH
client = vision.ImageAnnotatorClient()

#class OCR:

def main(bounding_box_info,category_index):
    #bounding_box_info gives path of file and information of its bounding boxes,classes and scores
    #category_index gives mapping for class name for classes provided in bounding box info
    #
    ocr_output=[]
    for image_info in bounding_box_info:
        file_name=image_info['image_path']
        #data dictionary is used for storing the extracted information for each field
        data=dict()
        data['Filename']=file_name.replace(STAGING_AREA+"/","")
        data['Filename']=data['Filename'].replace("unlabelled","labelled")
        data['timestamp']=int(time.time()*1000)
        for boxes_info in image_info['bounding_box_info']:
                
            class_=boxes_info['class_']
            score=boxes_info['score']
            category=CATEGORY[category_index[class_]['name']]
            
            image1 = Image.open(file_name)
            #getting dimensions of bounding boxes
            im_width, im_height = image1.size
            ymin,xmin,ymax,xmax =boxes_info['box']
            bb = (xmin * im_width, ymin * im_height, xmax * im_width, ymax * im_height)
            yminn,xminn,ymaxx,xmaxx = xmin * im_width, xmax * im_width , ymin * im_height , ymax * im_height
            #cropping the image to size of bounding box
            crop_img = image1.crop(bb)
            #saving cropped image to temporary location
            crop_img.save(STAGING_AREA+"/"+OCR_OUTPUT_IMAGE, crop_img.format)
            
            with io.open(STAGING_AREA+"/"+OCR_OUTPUT_IMAGE, 'rb') as image_file:
                content = image_file.read()
            #After reading the contents of the api,delete the cropped image from temporary location    
            os.remove(STAGING_AREA+"/"+OCR_OUTPUT_IMAGE)  
            
            image = vision.types.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations
            #list_content is used to save contents of cropped image
            list_content=[]
            for text in texts:
                list_content.append(text.description)
            if (len(list_content)>0):  
                value=list_content[0].split(":")[-1]
                value=value.split("\n")[-2]
                data[category]=value
            
        ocr_output.append(data)    
    return ocr_output      
        

    #pass

# def action(self):
"""
Extract data and push to Datastore
"""
        
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
    
    #Converting bb_info in desired format and push it to datastore
    bb_info_data=[]
    
    for image_info in bounding_box_info:
        file_name=image_info['image_path']
        #original width and height of image divided by resized height and width(1000,1000) of image
        width=image_info['image_width']
        height=image_info['image_height']
        #data dictionary is used for storing the extracted information for each field
        data=dict()
        json={}
        image_path=file_name.replace(STAGING_AREA+"/","")
        image_path=image_path.replace("unlabelled","labelled")
        data['Filename']=image_path
        key=image_path
        
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
            xminn,yminn,xmaxx,ymaxx = xmin *width, ymin *height, xmax * width, ymax *height
            #cropping the image to size of bounding box
            crop_img = image1.crop(bb)
            #saving cropped image to temporary location
            crop_img.save(STAGING_AREA+"/"+OCR_OUTPUT_IMAGE, crop_img.format)
            
            if boxes_info or boxes_info!='' or boxes_info!=None:
                class_id=boxes_info['class_']
                class_name=CATEGORY[category_index[class_id]['name']]

                points={"xmin":xminn,"xmax":xmaxx,"ymin":yminn,"ymax":ymaxx}
                json[class_name]=points
                
            
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
                
        if bool(json):        
            dict_={"key":key, "json":json, "timestamp":int(time.time()*1000),"automated":True}    
            bb_info_data.append(dict_)      
        ocr_output.append(data)    
    return ocr_output , bb_info_data     
        

    #pass

# def action(self):
"""
Extract data and push to Datastore
"""
        
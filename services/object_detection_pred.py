######## Image Object Detection Using Tensorflow-trained Classifier #########
#
# Description: 
# This program uses a TensorFlow-trained classifier to perform object detection.
# It loads the classifier uses it to perform object detection on an image.
# It draws boxes and scores around the objects of interest in the image.

## Some of the code is copied from Google's example at
## https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb

## and some is copied from Dat Tran's example at
## https://github.com/datitran/object_detector_app/blob/master/object_detection_app.py
# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import sys
from PIL import Image
from matplotlib import pyplot as plt
from vars_ import *

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
#os.getcwd()
# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util
class predict():
    def __init__(self,path_frozen_graph,path_labels,num_classes):   
        # Path to frozen detection graph .pb file, which contains the model that is used
        # for object detection
        self.i = 0
        self.PATH_TO_FROZEN_GRAPH = path_frozen_graph
        # Path to label map file(the pbtxt file)
        self.PATH_TO_LABELS = path_labels
        # Path to image
        #PATH_TO_IMAGE = os.path.join(CWD_PATH,IMAGE_NAME)
        # Number of classes the object detector can identify
        self.NUM_CLASSES = num_classes
        # Load the label map.
        # Label maps map indices to category names, so that when our convolution
        # network predicts `5`, we know that this corresponds to `king`.
        # Here we use internal utility functions, but anything that returns a
        # dictionary mapping integers to appropriate string labels would be fine
        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map,max_num_classes=self.NUM_CLASSES,use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)
        self.detection_graph = tf.Graph()
        self.sess=self.load_graph()    
    
    
    # Load the Tensorflow model into memory.
    def load_graph(self):
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            sess = tf.Session(graph=self.detection_graph)
            return sess    
    
    def run_for_single_image(self,image_expanded,batch):
        # Define input and output tensors (i.e. data) for the object detection classifier

        # Input tensor is the image
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        ocr_list=[]
        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')

        # Number of objects detected
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = self.sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: image_expanded})
      
        for image, box, score, class_,image_path in zip(image_expanded, boxes, scores, classes,batch):
                image1 = Image.open(image_path)
                im_width, im_height = image1.size
                
                vis_util.visualize_boxes_and_labels_on_image_array(
                image,
                np.squeeze(box),
                np.squeeze(class_).astype(np.int32),
                np.squeeze(score),
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=8,
                min_score_thresh=0.80)
                bounding_boxes_info = []
                for box,class_,score in zip(box[score>=0.2],class_[score>=0.2],score):
                    ocr_inputs={'box':box,'class_':class_,'score':score}
                    bounding_boxes_info.append(ocr_inputs)
                    
                #print image_path
                cv2.imwrite(image_path,image)
                ocr_list.append({'image_path': image_path, 'bounding_box_info':bounding_boxes_info})
                self.i += 1
        return ocr_list     

    
    def draw_vis(self,image,boxes,classes,scores):
        # Draw the results of the detection (aka 'visulaize the results')
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_expanded,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.80)
        
        cv2.imwrite(STAGING_AREA+"/"+'prediction1.jpg',image_expanded)
    
    def start(self,path_to_image):
        image = cv2.imread(path_to_image)
        image_expanded = np.expand_dims(image, axis=0)
        
        #np.expand_dims(image, axis=0)
        #boxes, scores, classes, num =self.run_for_single_image(image,image_expanded)
        #self.draw_vis(image, boxes , scores, classes)
        var=self.run_for_single_image(image_expanded)
        return var
        
    
    def read_from_list(self,path_list):
        ocr=[]
        batchsize=5
        for i in xrange(0, len(path_list), batchsize):
            batchsize=min(batchsize,len(path_list)-i+1)
            batch = path_list[i:i+batchsize]
            image_expanded=[]
            image_list=[]
            for i in batch:
                image=cv2.imread(i)
                image=cv2.resize(image,(1000,1000))
                image_expanded.append(image)
                
            ocr_list= self.run_for_single_image(np.array(image_expanded),batch)
            ocr.extend(ocr_list)
            #print ocr_list
        return ocr    


            
            
def main(image_list): 
    obj=predict(STAGING_AREA+"/"+FROZEN_GRAPH1,STAGING_AREA+"/"+LABEL_MAP,NUM_CLASSES)
    #path_list=['/home/sgrover/models/research/object_detection/images/test/267139_2017-0.jpg']
    category_index=obj.category_index  
    ocr=obj.read_from_list(image_list)
    #pred=obj.start('data/unlabelled/Anthem.1/Anthem.1-page1.jpg')
    return category_index,ocr
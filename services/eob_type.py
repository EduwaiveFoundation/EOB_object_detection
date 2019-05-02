import argparse
import os
import tensorflow as tf
import tensorflow_hub as hub
import pathlib
import json
from pathlib import *
from google.cloud import storage
#from env_vars import *
#l = tf.keras.layers
tf.enable_eager_execution()

def _img_string_to_tensor(image_string, image_size=(224, 224)):
    """Decodes jpeg image bytes and resizes into float32 tensor
    
    Args:
      image_string: A Tensor of type string that has the image bytes
    
    Returns:
      float32 tensor of the image
    """
    image_decoded = tf.image.decode_jpeg(image_string, channels=3)
    # Convert from full range of uint8 to range [0,1] of float32.
    image_decoded_as_float = tf.image.convert_image_dtype(image_decoded, dtype=tf.float32)
    # Resize to expected
    image_resized = tf.image.resize_images(image_decoded_as_float, size=image_size)
    
    return image_resized

def _path_to_img(path,image_size=(224, 224)):
        """From the given path returns a feature dictionary and label pair
        
        Args:
          path: A Tensor of type string of the file path to read from
          
        Returns:
          Tuple of dict and tensor. 
          Dictionary is key to tensor mapping of features
          Label is a Tensor of type string that is the label for these features
        """
        #label = tf.string_split([path], delimiter='/').values[-2]
        print path
        # Read in the image from disk
        image_string = tf.io.read_file(path)
        image_resized = _img_string_to_tensor(image_string, image_size)
        image=image_resized.numpy()
        #dict_images={path:image.tolist()}
        return image.tolist()
        
def prediction(export_dir,image_dictionary):
    with tf.Session(graph=tf.Graph()) as sess:
        tf.saved_model.loader.load(sess, ["serve"], export_dir)
        graph = tf.get_default_graph()
        #print(graph.get_operations())
        output = sess.run('dense/BiasAdd:0',
                   feed_dict={'Placeholder:0': image_dictionary.values()}
                )
        return output
    
def get_eob_type(imgs_folder):
    LABELS=['Anthem A', 'Blue Shield of CA', 'Anthem B', 'Anthem-BlueCross', 'WGS', 'Beacon', 'DeltaDental - SAG', 'SAG-AFTRA', 'DGA']
    images_path=[]
    #list of images to be classified
    images=os.listdir(imgs_folder)
    for image in images:
        if image.endswith('jpg') or image.endswith('jpeg'):
            image_path=imgs_folder+"/"+image
            images_path.append(image_path)

    #image_dictionary gives key as path to image and value as its array
    image_dictionary={}
    for image in images_path:
        image_dictionary[image] = _path_to_img(image)
    #TODO
    #need to write a function which automatically used latest model from the model_directory
    #path to saved model
    export_dir = '/home/navneet/Classification1/EOBType_Classification/data/run1/export/exporter/1556446318' 
    #make_predictions
    output=prediction(export_dir,image_dictionary) 
    #image_label gives path to image with its label
    #print output
    image_label={key:LABELS[value.index(max(value))] for key,value in zip(image_dictionary.keys(), output.tolist()) } 
    #with open(STAGING_AREA+"/"+'eob_type_classification_result.json', 'a') as outfile:  
     #  json.dump(image_label, outfile)
    #print image_label    
    #return image_label
    labels = image_label.values()
    count = {labels.count(i): i for i in labels}
    return count[max(count.keys())]
    
    
import argparse
import os
import tensorflow as tf
from google.cloud import storage
from env_var import *
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
        label = tf.string_split([path], delimiter='/').values[-2]

        # Read in the image from disk
        image_string = tf.io.read_file(path)
        image_resized = _img_string_to_tensor(image_string, image_size)
        image=image_resized.numpy()
        #dict_images={path:image.tolist()}
        return image.tolist()

    
def list_blobs(bucket_name,prefix):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix)
    labels=[]
    for blob in blobs:
        if blob.name.endswith(".jpg"):
            labels.append(blob.name)
    return labels

def download_blob(bucket_name, source_blob_name):
    """Downloads a list of blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    local_img_path=[]
    for f in source_blob_name:
        blob = bucket.blob(f)
        directories=f.split("/")
        no_dir=len(directories)
        parent_dir=STAGING_AREA
        for i in range(no_dir-1):
            if not parent_dir:
                parent_dir=parent_dir+directories[i] 
            else:
                parent_dir=parent_dir+"/"+directories[i]
            if(not os.path.exists(parent_dir)):
                os.mkdir(parent_dir)
        blob.download_to_filename(STAGING_AREA+"/"+f)
        local_img_path.append(STAGING_AREA+"/"+f)
        return local_img_path
        
def prediction(export_dir,image_dictionary):
    with tf.Session(graph=tf.Graph()) as sess:
        tf.saved_model.loader.load(sess, ["serve"], export_dir)
        graph = tf.get_default_graph()
        #print(graph.get_operations())
        output = sess.run(INPUT_TENSOR,
                   feed_dict={OUTPUT_TENSOR: image_dictionary.values()}
                )
        return output
    
def main(imgs_folder):
    bucket=imgs_folder.replace("gs://","").split("/")[0]
    folder=imgs_folder.replace("gs://","").split("/",1)[-1]
    #path to images to be classified
    images_path=list_blobs(bucket,folder)
    images_path=download_blob(bucket,images_path)
    #image_dictionary gives key as path to image and value as its array
    image_dictionary={}
    for image in images_path:
        image_dictionary[image] = _path_to_img(image)

    #TODO
    #need to write a function which automatically used latest model from the model_directory
    #path to saved model
    export_dir = STAGING_AREA+"/"+CLASSIFICATION_MODEL_DIR 
    #make_predictions
    output=prediction(export_dir,image_dictionary) 
    #image_label gives path to image with its label
    #print output
    image_label={key:(CLASSIFICATION_LABEL_USEFUL if value < 0 else CLASSIFICATION_LABEL_NOT_USEFUL) for key,value in                  zip(image_dictionary.keys(), output) }     
    return image_label

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
      '--img_path',
      help='location to images which needs to be classified',
      required=True
  )
    
    args = parser.parse_args()
    main(imgs_folder=args.img_path)
#converts images into encoded_image_string_tensors for online prediction
import os,json
import cv2
import tensorflow as tf
from vars_ import *
#from controller.tasks import IMAGE_PATH
#l = tf.keras.layers
tf.enable_eager_execution()

def _img_string_to_tensor(image_string,image_size):
    """Decodes jpeg image bytes and resizes it 
    
    Args:
      image_string: A Tensor of type string that has the image bytes
    
    Returns:
      encoded image string tensor of the image
    """
    image_decoded = tf.image.decode_jpeg(image_string, channels=3)
    # Convert from full range of uint8 to range [0,1] of float32.
    #image_decoded_as_float = tf.image.convert_image_dtype(image_decoded, dtype=tf.float32)
    # Resize to expected
    #image_resized = tf.image.resize_images(image_decoded_as_float, size=image_size)
    image_resized = tf.image.resize_images(image_decoded, size=image_size)
    
    return image_resized

def _path_to_img(path,image_size):
        """From the given path returns a feature dictionary and label pair
        
        Args:
          path: A Tensor of type string of the file path to read from
          
        Returns:
          encoded image string tensor of the image
        """
        label = tf.string_split([path], delimiter='/').values[-2]

        # Read in the image from disk
        image_string = tf.io.read_file(path)
        image_resized = _img_string_to_tensor(image_string, image_size)
        image=image_resized.numpy()
        #dict_images={path:image.tolist()}
        
        return {"inputs":image.tolist()}
    
def main(list_):   
    input_image_path=[]
    for image in list_:
        if image.endswith(".jpg") and "resized" not in image:
            print "input function"
            print image
            img = cv2.imread(image)
            #resizing the image to factor of 0.1 to have all images under size limit for inputs of online predictions
            res = cv2.resize(img,None,fx=.1, fy=.1)
            #saving the resized image in same directory where the original image is saved
            cv2.imwrite("{}/resized_{}".format(image.rsplit("/",1)[0],image.rsplit("/",1)[-1]),res)
            path = "{}/resized_{}".format(image.rsplit("/",1)[0],image.rsplit("/",1)[-1])
            height, width, channels = res.shape
            print width,height
            print path
            #convert the resized image into desired format
            ans = _path_to_img(path,(height,width))
            #get the image name
            path = path.split("/")[-1].replace(".jpg","")
            if not os.path.exists("data"):
                os.mkdir("data")
            if not os.path.exists(ENCODED_IMAGE_STRING_TENSOR_PATH):
                os.mkdir(ENCODED_IMAGE_STRING_TENSOR_PATH)
            #save the input image format into a file    
            with open("{}/inputs_{}.json".format(ENCODED_IMAGE_STRING_TENSOR_PATH,path),"wb") as fp:
                fp.write(json.dumps(ans)) 
            #append the dictionary with values path of image and path to file where it is stored in input image format in list   
            input_image_path.append({"image_path":image,
                                     "image_string_tensor":"{}/inputs_{}.json".format(ENCODED_IMAGE_STRING_TENSOR_PATH,path)})
    return input_image_path        
            
                
                

 
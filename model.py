#imports
import tensorflow as tf
import time, os, glob
from utils import load_image
from keras.preprocessing.image import ImageDataGenerator
import config, json
import numpy as np
import keras
from keras.models import load_model
from keras.utils import CustomObjectScope
from keras.initializers import glorot_uniform
from keras.models import model_from_json

from tensorflow.keras.callbacks import ModelCheckpoint as ModelCheckpoint
from keras.callbacks import ModelCheckpoint as ModelCheckpoint1

import logging, monitor
logging.basicConfig(level=logging.INFO)

class Model(object):
    """
    Wrapper for keras model for image classification 
    """
    def __init__(self, model_dir, train_dir=None, train=False, valid_dir=None):
        """
        Args:
            model_dir: (str), Directory to export saved model, or load saved model. 
            train_dir: (str), Directory for images to be trained
            train: (bool), for training mode or prediction mode
            valid_dir: (str), Directory for validation data.
        """
        self.train_dir = train_dir
        self.model_dir = model_dir
        self.valid_dir = valid_dir
        self.prev_classes=None
        #TODO:
        #Read from classes.txt
        with open('classes.txt') as json_file:
            data = json.load(json_file)
            self.classes = {int(i):data[i] for i in data.keys()}
        
        
        #In prediction mode
        try:
            if not train:
                with open('classes.txt') as json_file:
                    data = json.load(json_file)
                    
                self.classes = {int(i):data[i] for i in data.keys()}
                self.model = self.load_model()
                self.model.load_weights(self.latest_weights())
        except Exception, err:
            logging.info(err)

    def load_model(self):
        classifier = tf.keras.models.Sequential()
        classifier.add(tf.keras.layers.Conv2D(32, (3, 3), input_shape=(64, 64, 3),
                        activation='relu'))
        classifier.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))
        classifier.add(tf.keras.layers.Conv2D(32, (3, 3), activation='relu'))
        classifier.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))
        classifier.add(tf.keras.layers.Flatten())
        classifier.add(tf.keras.layers.Dense(units=128, activation='relu'))
        classifier.add(tf.keras.layers.Dense(units=len(self.classes), activation='softmax'))  
        return classifier
    
    #def load_model(self):
        

    def data_generator(self):
        train_imagedata = ImageDataGenerator(rescale=1. / 255, shear_range=0.2,
          zoom_range=0.2, horizontal_flip=True)
        test_imagedata = ImageDataGenerator(rescale=1. / 255)
        training_set = \
            train_imagedata.flow_from_directory(self.train_dir
                , target_size=(64, 64), batch_size=2, class_mode='categorical')
        
        #TODO:
        #handle if validation data not present
        test_set = \
            test_imagedata.flow_from_directory(self.valid_dir
                , target_size=(64, 64), batch_size=2, class_mode='categorical')
        #Update the config when this method is invoked
        #reverse the mapping
        self.prev_classes=len(self.classes)
        self.classes = {j:i for i,j in zip(training_set.class_indices.keys(), 
                               training_set.class_indices.values()) }
        error=None
        if self.prev_classes>len(self.classes):
            error="Invalid classes"
        with open('classes.txt', 'w') as outfile:
            json.dump(self.classes, outfile)
        return error,training_set, test_set 


    def train(self):
        """
        Starts training model and returns history logs
        """
        
        
        error,training_set, test_set=self.data_generator()
        if error:
            return "Invalid classes"
        print self.classes
        #tpu_model = tf.contrib.tpu.keras_to_tpu_model(model , strategy=tf.contrib.tpu.TPUDistributionStrategy(tf.contrib.cluster_resolver.TPUClusterResolver(tpu='grpc://' + os.environ['COLAB_TPU_ADDR'])))
        #t = time.localtime()
        #timestamp = time.strftime('%b-%d_%H%M', t)
        filepath=os.path.join(self.model_dir , '{epoch:02d}.h5')
        ##model.compile(tf.train.AdamOptimizer(), loss='categorical_crossentropy',metrics=['accuracy'])
        if(len(glob.glob(os.path.join(self.model_dir, "*.h5"))) == 0):
            print 1
            model=self.load_model()
            model.compile(tf.train.AdamOptimizer(), loss='categorical_crossentropy',metrics=['accuracy'])
            #checkpoint
            checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
            callbacks_list = [checkpoint]

            # fit the model
            history = model.fit(training_set, validation_data=test_set, epochs=10, batch_size=5, callbacks=callbacks_list)
            list_of_files = glob.glob(os.path.join(self.model_dir, "*.h5")) # * means all if need specific format then *.csv
            latest_file = max(list_of_files, key=os.path.getctime)
            self.export_model(model , latest_file.split('/')[-1])
        else :
            print 2
            # load the model
            list_of_files = glob.glob(os.path.join(self.model_dir, "*.h5")) # * means all if need specific format then *.csv
            latest_file = max(list_of_files, key=os.path.getctime)
            print (latest_file)
            #with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
            #    model = load_model(latest_file)
            with open('model1.txt') as json_file:
                json_string = json.load(json_file)
            with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
                model = model_from_json(json_string)    
                
            model.compile(tf.train.AdamOptimizer(), loss='categorical_crossentropy',metrics=['accuracy'])    
            #model=load_model(latest_file)
            model.load_weights(latest_file)
            print len(self.classes)
            print self.prev_classes
            if len(self.classes)!=self.prev_classes:
                last_layer = model.layers[-2].output
                output = keras.layers.Dense(len(self.classes), activation="softmax")(last_layer) 
                model = keras.models.Model(inputs=model.inputs, outputs=output)
                model.compile(tf.train.AdamOptimizer(), loss='categorical_crossentropy',metrics=['accuracy'])
                
                #model.add(keras.layers.Dense(units=len(self.classes), activation='softmax')) # fit the model
            checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
            callbacks_list = [checkpoint]
            history = model.fit_generator(training_set,epochs=100, steps_per_epoch=20, callbacks=callbacks_list)

            self.model = model
            self.export_model(model , latest_file.split('/')[-1])
            return history

    def export_model(self, model , file_name):
        """
        Exports model weights with current timestamp in (.h5) format 
        """
        t = time.localtime()
        timestamp = time.strftime('%b-%d_%H%M', t)
        model.save_weights(os.path.join(self.model_dir, file_name))#timestamp+'.h5'))
        json_string = model.to_json()
        with open('model1.txt', 'w') as outfile:
            json.dump(json_string, outfile)

    def latest_weights(self):  
        """
        Gets latest weight file from directory
        Weight file type: .h5
        """
        list_of_files = glob.glob(os.path.join(self.model_dir, "*.h5")) # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        #latest_file='model_dir/10.h5'
        print(latest_file)
        return latest_file
   
    def predict(self, img_path):
        """
        Predicts class label for image
        """
        img_tensor = load_image(img_path)
        #return self.classes[self.model.predict_classes(img_tensor)[0]]
        #img_tensor = load_image(img_path)
        threshold=0.9
        prob=self.model.predict(img_tensor)
        i,j = np.unravel_index(prob.argmax(), prob.shape)
        if prob[i,j]>threshold:
            return self.classes[self.model.predict_classes(img_tensor)[0]], prob[i,j]
        else:
            return "Unclassified", prob[i,j]
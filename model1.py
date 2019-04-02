import os
import tensorflow as tf
import tensorflow_hub as hub
import logging
from google.cloud import storage
tf.logging.set_verbosity(tf.logging.DEBUG)

l = tf.keras.layers

def list_blobs(bucket_name,prefix):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix)
    labels=[]
    for blob in blobs:
        labels.append(blob.name)
    return labels 

def list_images(bucket_name,prefix):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs(prefix=prefix)
    labels=[]
    for blob in blobs:
        if(blob.name.endswith(".jpg")):
            img="gs://{}/".format(bucket)
            labels.append(img+blob.name)
    return labels 

def _img_string_to_tensor(image_string, image_size=(299, 299)):
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

def make_dataset(file_pattern, image_size=(299, 299), shuffle=False, batch_size=64, num_epochs=None, buffer_size=4096):
    """Makes a dataset reading the input images given the file pattern
    
    Args:
      file_pattern: File pattern to match input files with
      image_size: size to resize images to
      shuffle: whether to shuffle the dataset
      batch_size: the batch size of the dataset
      num_epochs: number of times to repeat iteration of the dataset
      buffer_size: size of buffer for prefetch and shuffle operations
    
    Returns:
      A tf.data.Dataset with dictionary of key to Tensor for features and label Tensor of type string
    """
    
    def _path_to_img(path):
        """From the given path returns a feature dictionary and label pair
        
        Args:
          path: A Tensor of type string of the file path to read from
          
        Returns:
          Tuple of dict and tensor. 
          Dictionary is key to tensor mapping of features
          Label is a Tensor of type string that is the label for these features
        """
        #print(path.dtype)
        # Get the parent folder of this file to get it's class name
        label = tf.string_split([path], delimiter='/').values[-2]
        print "label:{}".format(label)
        # Read in the image from disk
        image_string = tf.io.read_file(path)
        image_resized = _img_string_to_tensor(image_string, image_size)
        #print(image_resized.dtype)
        #print(image_resized.get_shape())
        return { 'image': image_resized }, label

    
    #opt = tf.data.Options()
    #opt.experimental_autotune = True
    #opt.experimental_map_and_batch_fusion = True
    #opt.experimental_shuffle_and_repeat_fusion = True
    bucket=file_pattern.replace("gs://","").split("/")[0]
    image_dir=file_pattern.replace("gs://","").split("/",1)[-1]
    images_list=list_images(bucket,image_dir)
    train_imgs = tf.constant(images_list)
    dataset = tf.data.Dataset.from_tensor_slices(train_imgs)
    #dataset = tf.data.Dataset.list_files(file_pattern)

    if shuffle:
        dataset = dataset.shuffle(buffer_size)

    #dataset = dataset.repeat(num_epochs)
    dataset = dataset.map(_path_to_img)
    dataset = dataset.batch(batch_size).prefetch(buffer_size)

    #dataset = dataset.with_options(opt)
    return dataset

def serving_input_fn():
    # Note: only handles one image at a time 
    feature_placeholders = {'image': 
                            tf.placeholder(tf.float32 , shape=(None,224, 224, 3))}
 
    return tf.estimator.export.ServingInputReceiver(feature_placeholders,feature_placeholders)

def model_fn(features, labels, mode, params):
    """tf.estimator model function implementation for retraining an image classifier from a 
    tf hub module
    
    Args:
      features: dictionary of key to Tensor
      labels: Tensor of type string
      mode: estimator mode
      params: dictionary of parameters
      
    Returns:
      tf.estimator.EstimatorSpec instance
    """
    is_training = mode == tf.estimator.ModeKeys.TRAIN
    module_trainable = is_training and params.get('train_module', False)

    module = hub.Module(params['module_spec'], trainable=module_trainable, name=params['module_name'])
    bottleneck_tensor = module(features['image'])
    
    NUM_CLASSES = len(params['label_vocab'])
    logit_units = 1 if NUM_CLASSES == 2 else NUM_CLASSES
    logits = l.Dense(logit_units)(bottleneck_tensor)
    #print NUM_CLASSES
    #print tf.gather(params['label_vocab], tf_look_up[tf.argmax(input=logits, axis=1)])
    #print params['label_vocab'][tf.argmax(input=logits, axis=1)]
    predictions = {
      # Generate predictions (for PREDICT and EVAL mode)
      #"classes":tf.gather(params['label_vocab], tf_look_up[tf.argmax(input=logits, axis=1)])
      "classes":logits,
      # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
      # `logging_hook`.
      "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
  }

    if NUM_CLASSES == 2:
        head = tf.contrib.estimator.binary_classification_head(label_vocabulary=params['label_vocab'])
    else:
        head = tf.contrib.estimator.multi_class_head(n_classes=NUM_CLASSES, label_vocabulary=params['label_vocab'])

    
    if mode == tf.estimator.ModeKeys.TRAIN or mode == tf.estimator.ModeKeys.EVAL:
        optimizer = tf.train.AdamOptimizer(learning_rate=params.get('learning_rate', 1e-3))
        return head.create_estimator_spec(
        features, mode, logits, labels, optimizer=optimizer )        
    
    loss = None
    rain_op = None
    evalmetrics = None    
    #export_outputs = {'predict_output': tf.estimator.export.PredictOutput({"score": predictions})} 
    return tf.estimator.EstimatorSpec(mode=mode,
        predictions=predictions)
    """return head.create_estimatorspec(
        mode=mode,
        predictions=predictions
        #loss=loss,
        #train_op=train_op,
    )"""
    
def train(data_directory,model_directory):
    """Run training operation
    """
    
    run_config = tf.estimator.RunConfig()
    
    #data_directory = get_data('Classification')
    #model_directory = 'Classification/run2'
    bucket=data_directory.replace("gs://","").split("/")[0]
    print "bucket:{}".format(bucket)
    data_dir=data_directory.replace("gs://","").split("/",1)[-1]
    print "data_dir:{}".format(data_dir)
    params = {
        'module_spec': 'https://tfhub.dev/google/imagenet/resnet_v2_50/feature_vector/1',
        'module_name': 'resnet_v2_50',
        'learning_rate': 1e-3,
        'train_module': False,  # Whether we want to finetune the module
        'label_vocab': list_blobs(bucket,data_dir)
    }

    """ classifier = tf.estimator.Estimator(
        model_fn=model_fn,
        model_dir=model_directory,
        config=run_config,
        params=params
    )"""

    classifier = tf.estimator.DNNEstimator(
        head = tf.contrib.estimator.binary_classification_head(label_vocabulary=params['label_vocab']),
        hidden_units = [32,16],
        feature_columns = [tf.feature_column.numeric_column('image', shape=(224, 224, 3))],
        model_dir=model_directory
    )
        
    input_img_size = hub.get_expected_image_size(hub.Module(params['module_spec']))
    
    ckpt = classifier.latest_checkpoint()
    if ckpt != None:
          ckpt = int(ckpt.split('.')[1].split('-')[1])  
    else:
          ckpt = 0

    train_files = "{}/train".format(data_directory)
    train_input_fn = lambda: make_dataset(train_files, image_size=input_img_size, batch_size=8, shuffle=True)
    train_spec = tf.estimator.TrainSpec(train_input_fn, max_steps=100)
    
    exporter = tf.estimator.LatestExporter('exporter', serving_input_fn)

    eval_files ="{}/valid".format(data_directory)
    eval_input_fn = lambda: make_dataset(eval_files, image_size=input_img_size, batch_size=1)
    eval_spec = tf.estimator.EvalSpec(eval_input_fn,exporters=exporter)

    tf.estimator.train_and_evaluate(classifier, train_spec, eval_spec)
    

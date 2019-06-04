import tensorflow as tf
import os
import shutil
from google.cloud import storage
# Assuming object detection API is available for use
from models.research.object_detection.utils.config_util import create_pipeline_proto_from_configs
from models.research.object_detection.utils.config_util import get_configs_from_pipeline_file
import exporter

def upload_blob(source_file_name, destination_blob_name,bucket_name="testeob",):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    files_=os.listdir(source_file_name)
    for file_ in files_:
        if os.path.isdir(source_file_name+"/"+file_):
            sub_files=os.listdir(source_file_name+"/"+file_)
            for sub_file_ in sub_files:
                blob = bucket.blob(destination_blob_name+"/"+file_+"/"+sub_file_)
                blob.upload_from_filename(source_file_name+"/"+file_+"/"+sub_file_)
        else:        
            blob = bucket.blob(destination_blob_name+"/"+file_)
            blob.upload_from_filename(source_file_name+"/"+file_)

def main(input_type):
    # Configuration for model to be exported
    config_pathname = "trainer/training_scripts/data/pipeline.config"

    # Input checkpoint for the model to be exported
    # Path to the directory which consists of the saved model on disk (see above)
    trained_model_dir = "trainer/training_scripts/data/training"

    # Create proto from model confguration
    configs = get_configs_from_pipeline_file(config_pathname)
    pipeline_proto = create_pipeline_proto_from_configs(configs=configs)

    # Read .ckpt and .meta files from model directory
    checkpoint = tf.train.get_checkpoint_state(trained_model_dir)
    input_checkpoint = checkpoint.model_checkpoint_path

    # Model Version
    model_version_id = 'v1'

    # Output Directory
    output_directory = "trainer/training_scripts/data/exported_model" + str(model_version_id)

    if os.path.isdir(output_directory):
        shutil.rmtree(output_directory)

    # Export model for serving
    exporter.export_inference_graph(input_type=input_type,pipeline_config=pipeline_proto,
                                        trained_checkpoint_prefix=input_checkpoint,output_directory=output_directory)
    if input_type == "image_tensor":
        shutil.copyfile(output_directory+"/frozen_inference_graph.pb",                                   "/home/navneet/Classification1/pipeline/data/frozen_inference_graph.pb")
    else :
        #Upload the model to gcs
        upload_blob(output_directory+"/saved_model","model_directory")
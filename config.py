#Configuration variables
prediction_source = "/home/navneet/test/gcs-bucket/sampleeob/SAG-AFTRA" #Directory containing images to be predicted/inferred by the prediction pipeline
output_dir = "output" #Directory where the images will be placed by the prediction pipeline
train_dir = 'data/train' #Directory where the training images will be placed
valid_dir = 'data/train' #Directory where the validation images will be placed. You can keep the same value as of train_dir
model_dir = "/home/navneet/EOBType_Classification/project/model_dir" #Directory containing model and where the model will be exported
epochs = 20 #Then number of iterations over the dataset the model has to train
BUCKET_NAME = 'testeob'
STAGING_AREA = 'data'
TEMP_AREA='data/temp/'
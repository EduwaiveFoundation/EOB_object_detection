#TODO: fetch latest files automatiocally for prediction (LOGS)
#IMAGE_PATH=""
INPUT_TENSOR="dense/BiasAdd:0"
OUTPUT_TENSOR="Placeholder:0"
CLASSIFICATION_LABEL_USEFUL="Useful_Image"
CLASSIFICATION_LABEL_NOT_USEFUL="Not_Useful_Image"
STAGING_AREA="data"
CLASSIFICATION_MODEL_DIR="1554210882"#Useful and Not Useful Classification
FROZEN_GRAPH1="frozen_inference_graph.pb"
LABEL_MAP="labelmap.pbtxt"
NUM_CLASSES=7
OCR_OUTPUT_IMAGE='temp.jpg'
CATEGORY={'subscriber_name':'SubscriberName','patient_name':'PatientName','total_billed_by_provider':'BilledAmount','claim_no':'Claim#','deductible':'AppliedToDeductible','benefit':'InsuranceBenefit','copay':'CoPay'}
BATCH_SIZE=10
#Bucket for datastore images
BUCKET="testeob"
ENCODED_IMAGE_STRING_TENSOR_PATH="data/inputs"
PROJECT_ID="ace-automated-clean-eobs"
MODEL_NAME="eob_object_detection"
#for storing outputs of online predictions
OUTPUT_PATH="data/outputs"

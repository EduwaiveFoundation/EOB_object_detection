#TODO: fetch latest files automatiocally for prediction (LOGS)
#IMAGE_PATH=""
INPUT_TENSOR="dense/BiasAdd:0"
OUTPUT_TENSOR="Placeholder:0"
CLASSIFICATION_LABEL_USEFUL="Useful_Image"
CLASSIFICATION_LABEL_NOT_USEFUL="Not_Useful_Image"
STAGING_AREA="data"
CLASSIFICATION_MODEL_DIR="1554210882"
FROZEN_GRAPH1="frozen_inference_graph.pb"
LABEL_MAP="labelmap.pbtxt"
NUM_CLASSES=6
OCR_OUTPUT_IMAGE='temp.jpg'
CATEGORY={'subscriber_name':'SubscriberName','patient_name':'PatientName','total_billed_by_provider':'BilledAmount','claim_no':'Claim#','deductible':'AppliedToDeductible','benefit':'InsuranceBenefit'}

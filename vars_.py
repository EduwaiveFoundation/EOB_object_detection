IMAGE_PATH="gs://sampleeob/unlabelled/Anthem.1/"
INPUT_TENSOR="dense/BiasAdd:0"
OUTPUT_TENSOR="Placeholder:0"
CLASSIFICATION_LABEL_USEFUL="Useful_Image"
CLASSIFICATION_LABEL_NOT_USEFUL="Not_Useful_Image"
STAGING_AREA="data"
CLASSIFICATION_MODEL_DIR="1554210882"
FROZEN_GRAPH1="data/frozen_inference_graph.pb"
LABEL_MAP="labelmap.pbtxt"
NUM_CLASSES=6
PREDICTION_OUTPUT_PATH="prediction_outputs"
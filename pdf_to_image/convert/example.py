# EXAMPLE
from HandlerFactory import HandlerFactory, GCSHandler
from PDFToJPG import PDFToJPG


#print (globals())
input_path="gs://sampleeob/Beacon"
output_path="gs://sampleeob/unlabelled"

input_key=input_path.split("/")[0]
output_key=output_path.split("/")[0]

input_dict={"gs:":'GCSHandler',
            "s3:":'AWSHandler',
            "local":'LocalHandler'}

# Create a GCS Handler from Abstract Handler Factory
gs = HandlerFactory.create(input_dict[input_key])

# Set the input and output sources
gs.__input__ = input_path.split("/",2)[-1]
gs.__output__ = output_path.split("/",2)[-1]

# Creating an instance of PDFToJPG class
pdf_api = PDFToJPG()

# Using GCS Handler as a strategy to read, download and upload to-and-from GCS.
pdf_api.__strategy__ = gs

# Now executing the Pipeline
pdf_list=pdf_api.read()
print pdf_list
local_pdf_list=[]
for pdf in pdf_list:
    local_pdf_location=pdf_api.download(pdf)
    local_pdf_list.append(local_pdf_location)
images_location_list=[]
for pdf in local_pdf_list:
    images_location=pdf_api.process(pdf)
    images_location_list.append(images_location)
#print images_location_list   
for images_list in images_location_list:
    print images_list
    for image in images_list:
        print image
        pdf_name=pdf_api.export(image)

# Setting strategy to None
#pdf_api.__strategy__ = None

# Now executing the pipeline
#pdf_api.read()
#pdf_api.process()
#pdf_api.export()

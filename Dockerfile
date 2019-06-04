# The first instruction is what image we want to base our container on
# We Use an ubuntu runtime as a parent image
FROM python:2.7

# create root directory for our project in the container
RUN mkdir /prediction_pipeline

# Set the working directory to /prediction_service
WORKDIR /prediction_pipeline

# add the current directory to the container as /app
ADD . /prediction_pipeline

#RUN apt-get update -y \
#    && apt-get install python-pip -y
#RUN pip install --upgrade pip 
#RUN sudo easy_install pip

ENV GOOGLE_APPLICATION_CREDENTIALS=ace-automated-clean-eobs-4a38f27dff8c.json

# execute everyone’s favorite pip command, pip install -r
RUN pip install -r requirements.txt

EXPOSE 8000
# execute the Django project
CMD gunicorn eob_project.wsgi --max-requests 20 --bind 0.0.0.0:8000 -t 300





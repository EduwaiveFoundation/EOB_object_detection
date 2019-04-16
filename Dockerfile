# The first instruction is what image we want to base our container on
# We Use an ubuntu runtime as a parent image
FROM ubuntu:16.04

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
#ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /prediction_service

# Set the working directory to /prediction_service
WORKDIR /prediction_service

# Copy the current directory contents into the container at /prediction_service


#RUN chmod 755 redis_installation_script.sh

#Install redis
#RUN ./redis_installation_script.sh
RUN apt-get update
RUN apt-get install build-essential tcl -y
RUN mkdir redis-stable 
COPY redis-stable redis-stable
WORKDIR redis-stable
RUN make
RUN make test
RUN make install
RUN systemctl start redis




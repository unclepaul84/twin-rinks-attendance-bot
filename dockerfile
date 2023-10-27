# this is an official Python runtime, used as the parent image
FROM python:3.9.18-slim
# set the working directory in the container to /app
WORKDIR /app
# add the current directory to the container as /app
ADD . /app
# install any additional packages your application needs as specified in requirements.txt
RUN pip install -r requirements.txt
# unblock port 80 for the Bottle app to run on
EXPOSE 80
# execute the Bottle app
CMD ["python", “app.py"]
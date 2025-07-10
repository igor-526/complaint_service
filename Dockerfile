FROM python:3.11
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y
COPY ./requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt
COPY ./src /src
WORKDIR src
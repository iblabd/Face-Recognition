# syntax=docker/dockerfile:1
FROM python:3.10.7-alpine
FROM ubuntu

WORKDIR /Face-Recognition
ADD . /Face-Recognition

RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y cmake
RUN apt-get install -y gfortran
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN pip3 install -r ./requirements.txt

COPY requirements.txt requirements.txt
COPY . .

# ENTRYPOINT [ "python3" ]
CMD ["python3", "app/app.py"]
# CMD ["app/app.py"]
#no basic auth credentials
#Error: docker push exited with Error: 1

#ImportError: libGL.so.1: cannot open shared object file: No such file or directory
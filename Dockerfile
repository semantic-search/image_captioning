FROM tensorflow/tensorflow:1.13.2-gpu-py3
RUN apt-get install -y python3-pip
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install wget
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get -y install libopencv-dev python3-opencv
RUN pip install opencv-contrib-python
RUN pip install numpy==1.16.1
RUN pip install nltk
RUN pip install numpy scipy matplotlib ipython jupyter pandas sympy nose
RUN pip install tqdm
RUN pip install flask
RUN pip install -U Werkzeug==0.16.0
RUN pip install scikit-image
RUN pip install flask-restplus
RUN mkdir image_caption
WORKDIR /root/image_caption
RUN apt-get -y install git
RUN git clone https://github.com/coldmanck/show-attend-and-tell
WORKDIR show-attend-and-tell
COPY captions_train2014 train
COPY captions_val2014 val
COPY model model
COPY main.py .
CMD flask run -h 0.0.0.0

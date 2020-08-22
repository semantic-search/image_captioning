FROM tensorflow/tensorflow:1.13.2-gpu-py3
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install wget
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get -y install libopencv-dev python3-opencv
RUN pip install opencv-contrib-python
RUN pip install numpy==1.16.1
RUN pip install nltk
RUN pip install numpy scipy matplotlib ipython jupyter pandas sympy nose
RUN pip install tqdm python-dotenv kafka-python redis
RUN pip install scikit-image
RUN apt-get -y install git
RUN git clone https://github.com/jainal09/show-attend-and-tell.git
WORKDIR show-attend-and-tell
COPY captions_train2014.json train
COPY captions_val2014.json val
COPY model model
COPY app.py .
CMD ["python", "app.py"]

FROM ubuntu:22.04

# Install Git
RUN apt-get update -y && \
    apt-get install -y git libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx nano

RUN git clone https://github.com/breiflor/E-Ink_PhotoFrame_Backend

WORKDIR E-Ink_PhotoFrame_Backend
#install requirements
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip && \
    pip3 install --upgrade pip  && \
    pip3 install -r requirements.txt

#include working dirs

#open ports
EXPOSE 1883 8883

ENV CONFIG_PATH=/E-Ink_PhotoFrame_Backend/config
ENV STORAGE_PATH=/E-Ink_PhotoFrame_Backend/storage
ENV PANEL_PATH=/E-Ink_PhotoFrame_Backend/panels

#execute script
CMD ["python3", "Configurator.py"]

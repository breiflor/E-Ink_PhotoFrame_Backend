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
#patch remi
RUN sed -i '43s/.*/import html/' /usr/local/lib/python3.10/dist-packages/remi/gui.py
RUN sed -i '44s/.*/unescape = html.unescape/' /usr/local/lib/python3.10/dist-packages/remi/gui.py
RUN  sed -i '30,42 d'  /usr/local/lib/python3.10/dist-packages/remi/gui.py
#include working dirs

#open ports
EXPOSE 8080 8081 1883

ENV CONFIG_PATH=/E-Ink_PhotoFrame_Backend/config
ENV STORAGE_PATH=/E-Ink_PhotoFrame_Backend/storage
ENV PANEL_PATH=/E-Ink_PhotoFrame_Backend/panels

#execute script
CMD ["python3", "Configurator.py"]

FROM ubuntu:22.04

# Install dependencies needed by OpenCV
RUN apt-get update -y && \
    apt-get install -y git libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx nano python3 python3-pip && \
    pip3 install --upgrade pip

# Create workdir
WORKDIR /E-Ink_PhotoFrame_Backend

# Copy requirement list and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application files
COPY . /E-Ink_PhotoFrame_Backend

# Open ports (MQTT and Web Uploader)
EXPOSE 1883 8883 8081

ENV CONFIG_PATH=/E-Ink_PhotoFrame_Backend/config
ENV STORAGE_PATH=/E-Ink_PhotoFrame_Backend/storage
ENV PANEL_PATH=/E-Ink_PhotoFrame_Backend/panels

# Execute script
CMD ["python3", "Configurator.py"]

from flask import Flask, request, render_template
import cv2
import numpy as np
from ImageHandler import *

app = Flask(__name__)
cbk = print
@app.route('/add')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    print(file.name)
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    cbk(image)
    return 'Bild erfolgreich hochgeladen!'

def set_cbk(callback):
    global cbk
    cbk = callback


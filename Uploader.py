from flask import Flask, request, render_template, redirect, url_for, send_file
import cv2
import numpy as np
import io
import os
from werkzeug.utils import secure_filename
from ImageHandler import ImageHandler
from PanelManager import PanelManager

app = Flask(__name__)
# We will inject these via setup_app
image_handler = None
panel_manager = None

def setup_app(imghandler_instance, panelmanager_instance):
    global image_handler, panel_manager
    image_handler = imghandler_instance
    panel_manager = panelmanager_instance

@app.route('/')
def index():
    if image_handler is None or panel_manager is None:
        return "App not initialized correctly", 500

    images = image_handler.list_images()
    panels = panel_manager.list_panels()
    panels_info = []

    for panel in panels:
        p_info = {
            "name": panel,
            "images": panel_manager.list_images_from_panel(panel),
            "refresh": panel_manager.get_refresh_time(panel)
        }
        panels_info.append(p_info)

    return render_template('index.html', images=images, panels_info=panels_info)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return 'No image part', 400

    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400

    image_name = request.form.get('image_name')
    if not image_name:
        image_name = file.filename

    # Read the image to memory
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    # Save the image temporarily to disk so image_handler can process it
    # Because ImageHandler currently expects a file path
    temp_path = "temp_upload_" + secure_filename(image_name)
    if not temp_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        temp_path += ".png"

    cv2.imwrite(temp_path, image)

    # Process and store
    image_handler.add_image(temp_path, image_name)

    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return redirect(url_for('index'))

@app.route('/image/<image_name>')
def get_image(image_name):
    # To display image, we get the cv2 image from handler and send it
    img_path = image_handler.img_name_to_png_path(image_name)
    if not img_path.exists():
        return "Image not found", 404

    img = image_handler.get_image(image_name)

    # Encode to png
    is_success, buffer = cv2.imencode(".png", img)
    io_buf = io.BytesIO(buffer)

    return send_file(io_buf, mimetype='image/png')

@app.route('/append_to_panel', methods=['POST'])
def append_to_panel():
    panel_name = request.form.get('panel_name')
    image_name = request.form.get('image_name')

    if panel_name and image_name:
        panel_manager.add_image_to_panel(panel_name, image_name)

    return redirect(url_for('index'))

@app.route('/remove_from_panel', methods=['POST'])
def remove_from_panel():
    panel_name = request.form.get('panel_name')
    image_name = request.form.get('image_name')

    if panel_name and image_name:
        panel_manager.remove_image_from_panel(panel_name, image_name)

    return redirect(url_for('index'))

import pytest
import io
import numpy as np
import cv2

# Mock ImageHandler and PanelManager before importing Uploader
import sys
from unittest.mock import MagicMock, patch
sys.modules['ImageHandler'] = MagicMock()
sys.modules['PanelManager'] = MagicMock()

from Uploader import app, setup_app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    mock_imghandler = MagicMock()
    mock_panelmanager = MagicMock()
    mock_imghandler.list_images.return_value = ["test.png"]
    mock_panelmanager.list_panels.return_value = ["panel1"]
    mock_panelmanager.list_images_from_panel.return_value = ["test.png"]
    mock_panelmanager.get_refresh_time.return_value = 60

    setup_app(mock_imghandler, mock_panelmanager)

    with patch('Uploader.render_template', return_value="Mocked Template"):
        response = client.get('/')
        assert response.status_code == 200
        assert b"Mocked Template" in response.data

def test_upload_route(client):
    mock_imghandler = MagicMock()
    mock_panelmanager = MagicMock()
    setup_app(mock_imghandler, mock_panelmanager)

    # Create a small dummy image
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.png', img)

    data = {
        'image': (io.BytesIO(img_encoded.tobytes()), 'test_image.png')
    }

    response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Because we return redirect to index
    assert response.status_code == 302
    mock_imghandler.add_image.assert_called_once()

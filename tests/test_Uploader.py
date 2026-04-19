import pytest
import io
import numpy as np
import cv2

# Mock ImageHandler before importing Uploader
import sys
from unittest.mock import MagicMock, patch
sys.modules['ImageHandler'] = MagicMock()

from Uploader import app, set_cbk

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    # This might fail if the template doesn't exist during the test
    # We can mock render_template to avoid needing the actual file
    with patch('Uploader.render_template', return_value="Mocked Template"):
        response = client.get('/add')
        assert response.status_code == 200
        assert b"Mocked Template" in response.data

def test_upload_route(client):
    # Create a small dummy image
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.png', img)

    mock_cbk = MagicMock()
    set_cbk(mock_cbk)

    data = {
        'image': (io.BytesIO(img_encoded.tobytes()), 'test_image.png')
    }

    response = client.post('/upload', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert b"Bild erfolgreich hochgeladen!" in response.data
    mock_cbk.assert_called_once()

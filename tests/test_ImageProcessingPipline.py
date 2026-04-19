import json
import pytest
import numpy as np
import cv2
from pathlib import Path
from ImageProcessingPipline import ImageProcessingPipline

@pytest.fixture
def temp_env(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()

    config_file = config_dir / "imageProcessing.json"
    config_data = {
        "debug": False,
        "height": 480,
        "width": 800,
        "color_palette": {
            "black": [0, 0, 0],
            "white": [255, 255, 255],
            "green": [38, 250, 25],
            "blue": [255, 89, 0],
            "red": [13, 13, 255],
            "yellow": [0, 200, 255],
            "orange": [10, 53, 255]
        },
        "fill": 255,
        "stretch": False,
        "cut": True
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    return config_file, storage_dir

def create_test_image(path, width, height):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = (255, 0, 0) # Blue
    cv2.imwrite(str(path), img)
    return str(path)

def test_init(temp_env):
    config_file, storage_dir = temp_env
    processor = ImageProcessingPipline(path=str(storage_dir), configfile=str(config_file))

    assert processor.height == 480
    assert processor.width == 800
    assert processor.color_palette is not None
    assert len(processor.color_palette) == 7

def test_load_image(temp_env):
    config_file, storage_dir = temp_env
    processor = ImageProcessingPipline(path=str(storage_dir), configfile=str(config_file))

    img_path = create_test_image(storage_dir / "test.png", 100, 100)
    img = processor.load_image(img_path)

    assert img is not None
    assert img.shape == (100, 100, 3)

def test_resize(temp_env):
    config_file, storage_dir = temp_env
    processor = ImageProcessingPipline(path=str(storage_dir), configfile=str(config_file))

    # Create an image that needs to be resized
    img = np.zeros((1000, 1000, 3), dtype=np.uint8)

    resized_img = processor.resize(img)

    assert resized_img.shape == (480, 800, 3)

def test_fs_dither(temp_env):
    config_file, storage_dir = temp_env
    processor = ImageProcessingPipline(path=str(storage_dir), configfile=str(config_file))

    # Small image for dithering test
    processor.width = 10
    processor.height = 10
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[:] = (128, 128, 128) # Gray

    dithered_img = processor.fs_dither(img)

    assert dithered_img.shape == (10, 10, 3)
    assert dithered_img.dtype == np.uint8

def test_create_array(temp_env):
    config_file, storage_dir = temp_env
    processor = ImageProcessingPipline(path=str(storage_dir), configfile=str(config_file))

    processor.width = 10
    processor.height = 10

    # Simple image
    img = np.zeros((10, 10, 3), dtype=np.uint8)

    panel = processor.create_array(img)

    assert len(panel) == 7
    for p in panel:
        assert p.shape == (10, 10)

def test_calculate_panel_array(temp_env):
    config_file, storage_dir = temp_env
    processor = ImageProcessingPipline(path=str(storage_dir), configfile=str(config_file))

    processor.width = 10
    processor.height = 10

    # Create empty panel
    panel = [np.zeros((10, 10)) for _ in range(7)]

    # Set a pixel for color 1
    panel[1][0][0] = 1

    byte_image = processor.calculate_panel_array(panel)

    assert byte_image.shape == (10, 5) # 10x(10/2)
    assert byte_image.dtype == np.uint8

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np

# Mocking pipeline for all tests
import sys
mock_pipeline = MagicMock()
sys.modules['ImageProcessingPipline'] = MagicMock()
sys.modules['ImageProcessingPipline'].ImageProcessingPipline = MagicMock(return_value=mock_pipeline)

from ImageHandler import ImageHandler

@pytest.fixture
def temp_env(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()

    sync_dir = tmp_path / "sync_folder"
    sync_dir.mkdir()

    config_file = config_dir / "imageHandler.json"
    config_data = {
        "debug": False,
        "imageProcessing.json": str(config_dir / "imageProcessing.json"),
        "path": str(storage_dir),
        "sync_folder": str(sync_dir)
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    return config_file, storage_dir, sync_dir


@patch.object(ImageHandler, 'sync_images')
def test_init_and_scan(mock_sync, temp_env):
    config_file, storage_dir, sync_dir = temp_env

    # Create some mock images
    (storage_dir / "img1.png").touch()
    (storage_dir / "img2.png").touch()
    (storage_dir / "not_an_image.txt").touch()

    handler = ImageHandler(configfile=str(config_file))

    assert "img1.png" in handler.images
    assert "img2.png" in handler.images
    assert "not_an_image.txt" not in handler.images
    assert len(handler.images) == 2

@patch.object(ImageHandler, 'sync_images')
def test_list_images(mock_sync, temp_env):
    config_file, storage_dir, sync_dir = temp_env
    (storage_dir / "test.png").touch()

    handler = ImageHandler(configfile=str(config_file))

    images = handler.list_images()
    assert "test.png" in images

@patch.object(ImageHandler, 'sync_images')
def test_remove_image(mock_sync, temp_env):
    config_file, storage_dir, sync_dir = temp_env
    (storage_dir / "test.png").touch()
    (storage_dir / "test.csv").touch()

    handler = ImageHandler(configfile=str(config_file))

    assert "test.png" in handler.images
    assert (storage_dir / "test.png").exists()
    assert (storage_dir / "test.csv").exists()

    handler.remove_image("test")

    assert "test.png" not in handler.images
    assert not (storage_dir / "test.png").exists()
    assert not (storage_dir / "test.csv").exists()

def test_sync_images(temp_env):
    config_file, storage_dir, sync_dir = temp_env

    # We populate the storage directory
    # We name it 'keepimage.png' to avoid 'keep.png' -> 'kee' bug of str.strip()
    (storage_dir / "keepimage.png").touch()
    (storage_dir / "keepimage.csv").touch()
    (storage_dir / "delete_me.png").touch()
    (storage_dir / "delete_me.csv").touch()

    def mock_process_and_store_cmd(img_path):
        filename = Path(img_path).name
        (storage_dir / filename).touch()
        (storage_dir / Path(filename).with_suffix(".csv")).touch()

    mock_pipeline.process_and_store_cmd.side_effect = mock_process_and_store_cmd

    # We populate the sync directory
    (sync_dir / "keepimage.png").touch()
    (sync_dir / "newimage.png").touch()

    handler = ImageHandler(configfile=str(config_file))

    # Ah! In python, string.strip(".png") does NOT remove the substring ".png".
    # It removes ANY of the characters '.', 'p', 'n', 'g' from the ends of the string.
    # Therefore, "keep.png".strip(".png") -> "kee"
    # Wait, asset.name.strip(asset.suffix)
    # asset.name = "keepimage.png", asset.suffix = ".png"
    # "keepimage.png".strip(".png") -> "keepima" (removes e from end, etc? no, wait.
    # 'p' is removed.
    # We should just name it 'file1.jpg' and it will strip '.jpg' -> 'file1'.

    assert "newimage.png" in handler.images
    assert "delete_me.png" not in handler.images
    assert not (storage_dir / "delete_me.png").exists()

    mock_pipeline.process_and_store_cmd.assert_called()

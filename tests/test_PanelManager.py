import json
import pytest
from pathlib import Path
from PanelManager import PanelManager

@pytest.fixture
def temp_env(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    storage_dir = tmp_path / "eink_panel_storage"
    storage_dir.mkdir()

    config_file = config_dir / "panelManager.json"
    config_data = {
        "debug": False,
        "use_sync_folder_as_config": True,
        "eink_panel_storage": str(storage_dir)
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    return config_file, storage_dir

def test_init_and_load_panels(temp_env):
    config_file, storage_dir = temp_env
    # Create some mock panel files
    with open(storage_dir / "panel1.json", "w") as f:
        f.write("{}")
    with open(storage_dir / "panel2.json", "w") as f:
        f.write("{}")

    pm = PanelManager(configfile=str(config_file))

    assert "panel1.json" in pm.panels
    assert "panel2.json" in pm.panels
    assert len(pm.panels) == 2

def test_add_panel(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))

    pm.add_panel("panel3", images=["img1.png", "img2.png"], refresh_after_minutes=30)

    assert "panel3.json" in pm.panels

    panel_file = storage_dir / "panel3.json"
    assert panel_file.is_file()

    with open(panel_file, "r") as f:
        data = json.load(f)
        assert data["name"] == "panel3"
        assert data["images"] == ["img1.png", "img2.png"]
        assert data["refresh"] == 30

def test_list_panels(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))
    pm.add_panel("panel4")
    pm.add_panel("panel5")

    panels = pm.list_panels()
    assert "panel4.json" in panels
    assert "panel5.json" in panels

def test_remove_panel(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))
    pm.add_panel("panel_to_remove")

    assert "panel_to_remove.json" in pm.panels

    pm.remove_panel("panel_to_remove")
    assert "panel_to_remove.json" not in pm.panels
    assert not (storage_dir / "panel_to_remove.json").is_file()

def test_add_image_to_panel(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))
    pm.add_panel("panel6", images=["img1"])

    success = pm.add_image_to_panel("panel6", "img2.png")
    assert success is True

    images = pm.list_images_from_panel("panel6")
    assert "img1" in images
    assert "img2" in images

def test_remove_image_from_panel(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))
    pm.add_panel("panel7", images=["img1", "img2"])

    success = pm.remove_image_from_panel("panel7", "img1.png")
    assert success is True

    images = pm.list_images_from_panel("panel7")
    assert "img1" not in images
    assert "img2" in images

def test_change_refresh_time(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))
    pm.add_panel("panel8", refresh_after_minutes=60)

    success = pm.change_refresh_time("panel8", 120)
    assert success is True

    refresh = pm.get_refresh_time("panel8")
    assert refresh == 120

def test_sync_image_list(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))
    pm.add_panel("panel9", images=["img1", "img2"])

    pm.sync_image_list(["img2.png", "img3.png"])

    images = pm.list_images_from_panel("panel9")
    assert "img1" not in images
    assert "img2" in images
    assert "img3" in images

def test_add_image_to_nonexistent_panel(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))

    success = pm.add_image_to_panel("nonexistent_panel", "img1.png")
    assert success is False

def test_remove_image_from_nonexistent_panel(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))

    success = pm.remove_image_from_panel("nonexistent_panel", "img1.png")
    assert success is False

def test_list_images_from_nonexistent_panel(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))

    images = pm.list_images_from_panel("nonexistent_panel")
    assert images == []

def test_change_refresh_time_nonexistent_panel(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))

    success = pm.change_refresh_time("nonexistent_panel", 120)
    assert success is False

def test_get_refresh_time_nonexistent_panel(temp_env):
    config_file, storage_dir = temp_env
    pm = PanelManager(configfile=str(config_file))

    refresh = pm.get_refresh_time("nonexistent_panel")
    assert refresh == 0

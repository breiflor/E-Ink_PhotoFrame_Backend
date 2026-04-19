import json
import pytest
from unittest.mock import MagicMock, patch
import datetime

@pytest.fixture
def temp_env(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    config_file = config_dir / "configurator.json"
    config_data = {
        "debug": False,
        "image_sync": True,
        "img_handler": "mocked_img_handler.json",
        "panel_Manager": "mocked_panel_manager.json"
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    return config_file

@patch('Configurator.ImageHandler')
@patch('Configurator.PanelManager')
@patch('Configurator.Eink_Panel')
@patch('Configurator.Configurator.loop')
def test_init(mock_loop, mock_eink_panel, mock_panel_manager, mock_image_handler, temp_env):
    config_file = temp_env

    # Configure mock PanelManager to return a list of panels
    instance = mock_panel_manager.return_value
    instance.list_panels.return_value = ["panel1", "panel2"]
    instance.eink_config_storage = "mocked_storage"

    from Configurator import Configurator
    configurator = Configurator(configfile=str(config_file))

    assert configurator.debug is False
    assert len(configurator.panel_handlers) == 2
    assert len(configurator.panels) == 2
    assert configurator.last_sync == datetime.datetime.today().day - 1

    mock_loop.assert_called_once()
    mock_image_handler.return_value.sync_images.assert_not_called()

@patch('Configurator.ImageHandler')
@patch('Configurator.PanelManager')
@patch('Configurator.Eink_Panel')
def test_loop_logic(mock_eink_panel, mock_panel_manager, mock_image_handler, temp_env):
    config_file = temp_env

    class BreakLoop(Exception): pass

    instance = mock_panel_manager.return_value
    instance.list_panels.return_value = []

    from Configurator import Configurator
    with patch('Configurator.Configurator.loop'):
        configurator = Configurator(configfile=str(config_file))

    configurator.last_sync = datetime.datetime.today().day - 1
    mock_image_handler.return_value.sync_images.return_value = ["img1.png"]

    with patch('time.sleep', side_effect=BreakLoop):
        try:
            configurator.loop()
        except BreakLoop:
            pass

    # Check that it synced images
    mock_image_handler.return_value.sync_images.assert_called_once()
    instance.sync_image_list.assert_called_once_with(["img1.png"])
    assert configurator.last_sync == datetime.datetime.today().day

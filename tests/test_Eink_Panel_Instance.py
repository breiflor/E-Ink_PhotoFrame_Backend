import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock ImageHandler and mqtt_client before importing Eink_Panel
import sys
sys.modules['ImageHandler'] = MagicMock()

import paho.mqtt.client as mqtt_client
mock_mqtt = MagicMock()
mqtt_client.Client = MagicMock(return_value=mock_mqtt)

from Eink_Panel_Instance import Eink_Panel

@pytest.fixture
def temp_env(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create MQTT config
    mqtt_config = config_dir / "mqtt_config1.cfg"
    mqtt_data = {
        "user": "test_user",
        "password": "test_password",
        "broker": "localhost",
        "port": 1883
    }
    with open(mqtt_config, "w") as f:
        json.dump(mqtt_data, f)

    # Create Panel config
    panel_config = tmp_path / "panel1.json"
    panel_data = {
        "name": "panel1",
        "refresh": 60,
        "current_image": "no data - waiting for panel connection",
        "images": ["img1", "img2"]
    }
    with open(panel_config, "w") as f:
        json.dump(panel_data, f)

    return panel_config, mqtt_config

@patch('Eink_Panel_Instance.Eink_Panel.load_next_image')
def test_init(mock_load_image, temp_env):
    mock_load_image.return_value = "mocked_image_data"
    panel_config, mqtt_config = temp_env

    # Make loop_forever non-blocking by mocking it
    mock_mqtt.loop_forever = MagicMock()

    panel = Eink_Panel(configfile=str(panel_config), mqtt_settings=str(mqtt_config))

    assert panel.config["name"] == "panel1"
    assert panel.state == "no Connection"
    assert panel.image == "mocked_image_data"

    # Check MQTT setup
    mock_mqtt.username_pw_set.assert_called_with("test_user", "test_password")
    mock_mqtt.connect.assert_called_with("localhost", 1883)
    mock_mqtt.loop_forever.assert_called_once()

@patch('Eink_Panel_Instance.Eink_Panel.load_next_image')
def test_on_connect(mock_load_image, temp_env):
    mock_load_image.return_value = "mocked_image_data"
    panel_config, mqtt_config = temp_env
    mock_mqtt.loop_forever = MagicMock()

    panel = Eink_Panel(configfile=str(panel_config), mqtt_settings=str(mqtt_config))

    panel.on_connect(mock_mqtt, None, None, 0)

    mock_mqtt.subscribe.assert_any_call("Eink_frame/panel1/ack")
    mock_mqtt.subscribe.assert_any_call("Eink_frame/panel1/reset")
    mock_mqtt.subscribe.assert_any_call("Eink_frame/panel1/get_image")
    assert mock_mqtt.on_message == panel.callback

@patch('Eink_Panel_Instance.Eink_Panel.load_next_image')
def test_callback_reset(mock_load_image, temp_env):
    mock_load_image.return_value = "mocked_image_data"
    panel_config, mqtt_config = temp_env
    mock_mqtt.loop_forever = MagicMock()

    panel = Eink_Panel(configfile=str(panel_config), mqtt_settings=str(mqtt_config))

    msg = MagicMock()
    msg.topic = "Eink_frame/panel1/reset"

    panel.callback(mock_mqtt, None, msg)

    assert panel.state == "WAIT"
    assert panel.last_update is None

@patch('Eink_Panel_Instance.Eink_Panel.load_next_image')
def test_img_request(mock_load_image, temp_env):
    mock_load_image.return_value = "mocked_image_data" * 1000 # Make sure it's long enough
    panel_config, mqtt_config = temp_env
    mock_mqtt.loop_forever = MagicMock()

    panel = Eink_Panel(configfile=str(panel_config), mqtt_settings=str(mqtt_config))
    panel.state = "WAIT"
    panel.last_update = None

    panel.img_request()

    assert panel.state == "SENT SECTION 1"
    mock_mqtt.publish.assert_called()

@patch('Eink_Panel_Instance.Eink_Panel.load_next_image')
def test_send_image_sequence(mock_load_image, temp_env):
    mock_load_image.return_value = "mocked_image_data" * 1000
    panel_config, mqtt_config = temp_env
    mock_mqtt.loop_forever = MagicMock()

    panel = Eink_Panel(configfile=str(panel_config), mqtt_settings=str(mqtt_config))

    # Step 1
    panel.state = "SENT SECTION 1"
    panel.send_image("1")
    assert panel.state == "SENT SECTION 2"

    # Step 8 to 9
    panel.state = "SENT SECTION 8"
    panel.next_image_name = "img1"
    panel.send_image("8")
    assert panel.state == "Update Status Infos"

    # Update Status Infos
    panel.send_image("9")
    assert panel.state == "WAIT"
    assert panel.last_update is not None

    # Verify config was updated
    with open(panel_config, "r") as f:
        data = json.load(f)
        assert data["current_image"] == "img1"

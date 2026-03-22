"""Shared pytest fixtures for retropie2600 tests.

All fixtures mock hardware interfaces so tests run on macOS
without Pi hardware (pigpio, evdev, uinput).
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_pigpio():
    """Mock pigpio.pi() instance for GPIO tests.
    
    Provides a MagicMock that simulates the pigpio.pi() interface:
    - set_mode(), set_pull_up_down(), set_glitch_filter()
    - callback() returns a cancellable mock callback handle
    - read() returns 1 by default (pin HIGH / pull-up)
    - connected property is True
    
    Usage:
        def test_something(mock_pigpio):
            monitor = GPIOMonitor(config, callback, pigpio_instance=mock_pigpio)
    """
    pi = MagicMock()
    pi.connected = True
    pi.read.return_value = 1  # default: pin HIGH (pull-up active)
    
    # callback() returns a handle with a cancel() method
    callback_handle = MagicMock()
    pi.callback.return_value = callback_handle
    
    # pigpio constants available on the mock
    pi.INPUT = 0
    pi.OUTPUT = 1
    pi.PUD_UP = 2
    pi.PUD_DOWN = 1
    pi.PUD_OFF = 0
    pi.EITHER_EDGE = 2
    pi.FALLING_EDGE = 1
    pi.RISING_EDGE = 0
    
    return pi


@pytest.fixture
def mock_evdev_uinput():
    """Mock evdev.UInput device for keyboard injection tests.
    
    Captures write() and syn() calls for assertion.
    
    Usage:
        def test_something(mock_evdev_uinput):
            # Inject key then assert:
            mock_evdev_uinput.write.assert_called_with(...)
    """
    ui = MagicMock()
    ui.write = MagicMock()
    ui.syn = MagicMock()
    ui.close = MagicMock()
    return ui


@pytest.fixture
def mock_socket():
    """Mock socket.socket for UDP command tests.
    
    Captures sendto() calls for assertion.
    
    Usage:
        def test_something(mock_socket):
            mock_socket.sendto.assert_called_with(b"SHADER_TOGGLE", ("127.0.0.1", 55355))
    """
    sock = MagicMock()
    sock.sendto = MagicMock()
    sock.close = MagicMock()
    return sock


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for shutdown command tests.
    
    Usage:
        def test_something(mock_subprocess):
            mock_subprocess.assert_called_once_with(["sudo", "shutdown", "-h", "now"], check=False)
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        yield mock_run


@pytest.fixture
def tmp_config(tmp_path):
    """Create a temporary valid switches.yaml config file.
    
    Returns the path to the temp config file.
    
    Usage:
        def test_something(tmp_config):
            config = Config.from_file(tmp_config)
    """
    config_content = """
switches:
  power:
    pin: 26
    type: toggle
    debounce_ms: 500
  tv_type:
    pin_color: 4
    pin_bw: 17
    type: toggle
    debounce_ms: 20
  game_select:
    pin: 22
    type: momentary
    debounce_ms: 5
  game_reset:
    pin: 27
    type: momentary
    debounce_ms: 5
  difficulty_left:
    pin_a: 23
    pin_b: 24
    type: toggle
    debounce_ms: 20
  difficulty_right:
    pin_a: 25
    pin_b: 5
    type: toggle
    debounce_ms: 20
  channel:
    pin_2: 6
    pin_3: 13
    type: toggle
    debounce_ms: 20

power_led:
  pin: 12

shader:
  retroarch_host: "127.0.0.1"
  retroarch_port: 55355

shutdown:
  command: "sudo shutdown -h now"
  delay_ms: 500

logging:
  level: INFO
"""
    config_file = tmp_path / "switches.yaml"
    config_file.write_text(config_content)
    return str(config_file)

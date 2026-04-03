from types import SimpleNamespace
from unittest.mock import MagicMock, call

from retropie2600.config import Config
from retropie2600.gpio_monitor import GPIOMonitor, SwitchEvent


def _mock_pigpio_module(mock_pi):
    return SimpleNamespace(
        INPUT=mock_pi.INPUT,
        PUD_UP=mock_pi.PUD_UP,
        EITHER_EDGE=mock_pi.EITHER_EDGE,
        pi=MagicMock(return_value=mock_pi),
    )


def _build_monitor(tmp_config, mock_pigpio, monkeypatch, callback=None):
    import retropie2600.gpio_monitor as gpio_monitor_module

    pigpio_module = _mock_pigpio_module(mock_pigpio)
    monkeypatch.setattr(gpio_monitor_module, "pigpio", pigpio_module)
    config = Config.from_file(tmp_config)
    monitor = GPIOMonitor(config=config, callback=callback or MagicMock(), pigpio_instance=mock_pigpio)
    return monitor, pigpio_module


def _registered_handler_for_pin(mock_pigpio, pin):
    for call_item in mock_pigpio.callback.call_args_list:
        if call_item.args[0] == pin:
            return call_item.args[2]
    raise AssertionError(f"No callback registered for pin {pin}")


def _single_pin_toggle_config(tmp_path):
    config_content = """
switches:
  power:
    pin: 26
    type: toggle
    positions:
      low: "on"
      high: "off"
    debounce_ms: 500
  tv_type:
    pin: 4
    type: toggle
    positions:
      low: bw
      high: color
    debounce_ms: 20
  game_select:
    pin: 22
    type: momentary
    debounce_ms: 5
"""
    config_file = tmp_path / "single_pin_switches.yaml"
    config_file.write_text(config_content)
    return str(config_file)


def test_start_registers_callbacks_for_all_pins(tmp_config, mock_pigpio, monkeypatch):
    monitor, pigpio_module = _build_monitor(tmp_config, mock_pigpio, monkeypatch)

    monitor.start()

    assert mock_pigpio.callback.call_count == 11
    for call_item in mock_pigpio.callback.call_args_list:
        assert call_item.args[1] == pigpio_module.EITHER_EDGE


def test_start_sets_pull_up_for_all_pins(tmp_config, mock_pigpio, monkeypatch):
    monitor, pigpio_module = _build_monitor(tmp_config, mock_pigpio, monkeypatch)

    monitor.start()

    expected_pins = [26, 4, 17, 22, 27, 23, 24, 25, 5, 6, 13]
    expected_calls = [call(pin, pigpio_module.PUD_UP) for pin in expected_pins]
    mock_pigpio.set_pull_up_down.assert_has_calls(expected_calls, any_order=True)
    assert mock_pigpio.set_pull_up_down.call_count == len(expected_pins)


def test_start_sets_glitch_filter(tmp_config, mock_pigpio, monkeypatch):
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch)

    monitor.start()

    expected_calls = [
        call(26, 500000),
        call(4, 20000),
        call(17, 20000),
        call(22, 5000),
        call(27, 5000),
        call(23, 20000),
        call(24, 20000),
        call(25, 20000),
        call(5, 20000),
        call(6, 20000),
        call(13, 20000),
    ]
    mock_pigpio.set_glitch_filter.assert_has_calls(expected_calls, any_order=True)
    assert mock_pigpio.set_glitch_filter.call_count == 11


def test_toggle_pin_low_emits_event(tmp_config, mock_pigpio, monkeypatch):
    callback = MagicMock()
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch, callback=callback)
    monitor.start()

    handler = _registered_handler_for_pin(mock_pigpio, 4)
    handler(4, 0, 123)

    callback.assert_called_once()
    event = callback.call_args.args[0]
    assert isinstance(event, SwitchEvent)
    assert event.switch_name == "tv_type"
    assert event.position == "color"
    assert isinstance(event.timestamp, float)


def test_toggle_pin_high_ignored(tmp_config, mock_pigpio, monkeypatch):
    callback = MagicMock()
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch, callback=callback)
    monitor.start()

    handler = _registered_handler_for_pin(mock_pigpio, 4)
    handler(4, 1, 123)

    callback.assert_not_called()


def test_momentary_pin_low_emits_pressed(tmp_config, mock_pigpio, monkeypatch):
    callback = MagicMock()
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch, callback=callback)
    monitor.start()

    handler = _registered_handler_for_pin(mock_pigpio, 22)
    handler(22, 0, 123)

    callback.assert_called_once()
    event = callback.call_args.args[0]
    assert event.switch_name == "game_select"
    assert event.position == "pressed"


def test_momentary_pin_high_emits_released(tmp_config, mock_pigpio, monkeypatch):
    callback = MagicMock()
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch, callback=callback)
    monitor.start()

    handler = _registered_handler_for_pin(mock_pigpio, 22)
    handler(22, 1, 123)

    callback.assert_called_once()
    event = callback.call_args.args[0]
    assert event.switch_name == "game_select"
    assert event.position == "released"


def test_read_all_states_returns_active_pins(tmp_config, mock_pigpio, monkeypatch):
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch)

    def read_side_effect(pin):
        if pin == 4:
            return 0
        return 1

    mock_pigpio.read.side_effect = read_side_effect
    monitor.start()

    assert monitor.read_all_states() == {"tv_type": "color"}


def test_stop_cancels_all_callbacks(tmp_config, mock_pigpio, monkeypatch):
    handles = [MagicMock() for _ in range(11)]
    mock_pigpio.callback.side_effect = handles
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch)
    monitor.start()

    monitor.stop()

    for handle in handles:
        handle.cancel.assert_called_once()


def test_graceful_degradation_no_pigpio(tmp_config, mock_pigpio, monkeypatch):
    import retropie2600.gpio_monitor as gpio_monitor_module

    monkeypatch.setattr(gpio_monitor_module, "pigpio", None)
    config = Config.from_file(tmp_config)
    monitor = GPIOMonitor(config=config, callback=MagicMock(), pigpio_instance=mock_pigpio)

    monitor.start()

    assert monitor._stub_mode is True


def test_graceful_degradation_pigpiod_not_connected(tmp_config, mock_pigpio, monkeypatch):
    mock_pigpio.connected = False
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch)

    monitor.start()

    assert monitor._stub_mode is True


def test_read_all_states_returns_empty_in_stub_mode(tmp_config, mock_pigpio, monkeypatch):
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch)
    monitor._stub_mode = True

    assert monitor.read_all_states() == {}


def test_single_pin_toggle_fires_on_low(tmp_path, mock_pigpio, monkeypatch):
    callback = MagicMock()
    config_path = _single_pin_toggle_config(tmp_path)
    monitor, _ = _build_monitor(config_path, mock_pigpio, monkeypatch, callback=callback)
    monitor.start()

    handler = _registered_handler_for_pin(mock_pigpio, 4)
    handler(4, 0, 123)

    callback.assert_called_once()
    event = callback.call_args.args[0]
    assert isinstance(event, SwitchEvent)
    assert event.switch_name == "tv_type"
    assert event.position == "bw"


def test_single_pin_toggle_fires_on_high(tmp_path, mock_pigpio, monkeypatch):
    callback = MagicMock()
    config_path = _single_pin_toggle_config(tmp_path)
    monitor, _ = _build_monitor(config_path, mock_pigpio, monkeypatch, callback=callback)
    monitor.start()

    handler = _registered_handler_for_pin(mock_pigpio, 4)
    handler(4, 1, 123)

    callback.assert_called_once()
    event = callback.call_args.args[0]
    assert isinstance(event, SwitchEvent)
    assert event.switch_name == "tv_type"
    assert event.position == "color"


def test_read_all_states_single_pin_toggle_returns_correct_position(tmp_path, mock_pigpio, monkeypatch):
    config_path = _single_pin_toggle_config(tmp_path)
    monitor, _ = _build_monitor(config_path, mock_pigpio, monkeypatch)
    monitor.start()

    mock_pigpio.read.return_value = 0
    assert monitor.read_all_states() == {"power": "on", "tv_type": "bw"}

    mock_pigpio.read.return_value = 1
    assert monitor.read_all_states() == {"power": "off", "tv_type": "color"}


def test_dual_pin_toggle_backward_compat_still_works(tmp_config, mock_pigpio, monkeypatch):
    monitor, _ = _build_monitor(tmp_config, mock_pigpio, monkeypatch)

    def read_side_effect(pin):
        if pin == 17:
            return 0
        return 1

    mock_pigpio.read.side_effect = read_side_effect
    monitor.start()

    assert monitor.read_all_states() == {"tv_type": "bw"}


def test_power_single_pin_toggle_fires_on_low(tmp_path, mock_pigpio, monkeypatch):
    callback = MagicMock()
    config_path = _single_pin_toggle_config(tmp_path)
    monitor, _ = _build_monitor(config_path, mock_pigpio, monkeypatch, callback=callback)
    monitor.start()

    handler = _registered_handler_for_pin(mock_pigpio, 26)
    handler(26, 0, 123)

    callback.assert_called_once()
    event = callback.call_args.args[0]
    assert isinstance(event, SwitchEvent)
    assert event.switch_name == "power"
    assert event.position == "on"


def test_power_single_pin_toggle_fires_on_high(tmp_path, mock_pigpio, monkeypatch):
    callback = MagicMock()
    config_path = _single_pin_toggle_config(tmp_path)
    monitor, _ = _build_monitor(config_path, mock_pigpio, monkeypatch, callback=callback)
    monitor.start()

    handler = _registered_handler_for_pin(mock_pigpio, 26)
    handler(26, 1, 123)

    callback.assert_called_once()
    event = callback.call_args.args[0]
    assert isinstance(event, SwitchEvent)
    assert event.switch_name == "power"
    assert event.position == "off"


def test_read_all_states_power_single_pin_toggle(tmp_path, mock_pigpio, monkeypatch):
    config_path = _single_pin_toggle_config(tmp_path)
    monitor, _ = _build_monitor(config_path, mock_pigpio, monkeypatch)
    monitor.start()

    mock_pigpio.read.return_value = 0
    states = monitor.read_all_states()
    assert states["power"] == "on"

    mock_pigpio.read.return_value = 1
    states = monitor.read_all_states()
    assert states["power"] == "off"

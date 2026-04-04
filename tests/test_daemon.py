import signal
import time
from unittest.mock import MagicMock

from retropie2600.gpio_monitor import SwitchEvent


def _build_daemon(tmp_config):
    from retropie2600.daemon import RetroPie2600Daemon

    return RetroPie2600Daemon(tmp_config)


def test_daemon_loads_config_and_initializes_subsystems(tmp_config, monkeypatch):
    from retropie2600 import daemon as daemon_module

    mock_config = MagicMock()
    mock_config.shader = {"retroarch_host": "127.0.0.1", "retroarch_port": 55355}
    mock_config.shutdown = {"command": "sudo shutdown -h now", "delay_ms": 500}

    mock_monitor = MagicMock()
    mock_monitor.read_all_states.return_value = {}
    mock_injector = MagicMock()
    mock_shader = MagicMock()
    mock_shutdown = MagicMock()
    mock_shutdown.is_shutting_down = False

    from_file_mock = MagicMock(return_value=mock_config)
    monkeypatch.setattr(daemon_module.Config, "from_file", from_file_mock)
    monitor_ctor = MagicMock(return_value=mock_monitor)
    injector_ctor = MagicMock(return_value=mock_injector)
    shader_ctor = MagicMock(return_value=mock_shader)
    shutdown_ctor = MagicMock(return_value=mock_shutdown)
    monkeypatch.setattr(daemon_module, "GPIOMonitor", monitor_ctor)
    monkeypatch.setattr(daemon_module, "InputInjector", injector_ctor)
    monkeypatch.setattr(daemon_module, "ShaderController", shader_ctor)
    monkeypatch.setattr(daemon_module, "ShutdownController", shutdown_ctor)
    mock_led = MagicMock()
    led_ctor = MagicMock(return_value=mock_led)
    monkeypatch.setattr(daemon_module, "PowerLED", led_ctor)

    daemon = _build_daemon(tmp_config)
    monkeypatch.setattr(daemon._shutdown_event, "wait", MagicMock(return_value=True))

    assert daemon.run() == 0

    from_file_mock.assert_called_once_with(tmp_config)
    injector_ctor.assert_called_once_with()
    shader_ctor.assert_called_once_with(host="127.0.0.1", port=55355)
    shutdown_ctor.assert_called_once_with(command="sudo shutdown -h now", delay_ms=500)
    monitor_ctor.assert_called_once()
    mock_monitor.start.assert_called_once_with()


def test_event_routing_power_off_calls_shutdown(tmp_config):
    daemon = _build_daemon(tmp_config)
    daemon._shutdown_controller = MagicMock()
    daemon._shutdown_controller.is_shutting_down = False

    daemon._on_switch_event(SwitchEvent("power", "off", time.time()))

    daemon._shutdown_controller.initiate_shutdown.assert_called_once_with()


def test_event_routing_channel_calls_shader(tmp_config):
    daemon = _build_daemon(tmp_config)
    daemon._shutdown_controller = MagicMock()
    daemon._shutdown_controller.is_shutting_down = False
    daemon._shader_controller = MagicMock()

    daemon._on_switch_event(SwitchEvent("channel", "on", time.time()))

    daemon._shader_controller.toggle_shader.assert_called_once_with()


def test_event_routing_game_select_pressed_calls_injector(tmp_config):
    daemon = _build_daemon(tmp_config)
    daemon._shutdown_controller = MagicMock()
    daemon._shutdown_controller.is_shutting_down = False
    daemon._input_injector = MagicMock()

    daemon._on_switch_event(SwitchEvent("game_select", "pressed", time.time()))

    daemon._input_injector.press_key.assert_called_once_with("game_select")


def test_event_routing_game_select_released_ignored(tmp_config):
    daemon = _build_daemon(tmp_config)
    daemon._shutdown_controller = MagicMock()
    daemon._shutdown_controller.is_shutting_down = False
    daemon._input_injector = MagicMock()

    daemon._on_switch_event(SwitchEvent("game_select", "released", time.time()))

    daemon._input_injector.press_key.assert_not_called()


def test_event_routing_tv_type_color(tmp_config):
    daemon = _build_daemon(tmp_config)
    daemon._shutdown_controller = MagicMock()
    daemon._shutdown_controller.is_shutting_down = False
    daemon._input_injector = MagicMock()

    daemon._on_switch_event(SwitchEvent("tv_type", "color", time.time()))

    daemon._input_injector.press_key.assert_called_once_with("tv_type_color")


def test_event_routing_difficulty_left_a(tmp_config):
    daemon = _build_daemon(tmp_config)
    daemon._shutdown_controller = MagicMock()
    daemon._shutdown_controller.is_shutting_down = False
    daemon._input_injector = MagicMock()

    daemon._on_switch_event(SwitchEvent("difficulty_left", "a", time.time()))

    daemon._input_injector.press_key.assert_called_once_with("difficulty_left_a")


def test_events_ignored_when_shutting_down(tmp_config):
    daemon = _build_daemon(tmp_config)
    daemon._shutdown_controller = MagicMock()
    daemon._shutdown_controller.is_shutting_down = True
    daemon._input_injector = MagicMock()
    daemon._shader_controller = MagicMock()

    daemon._on_switch_event(SwitchEvent("channel", "on", time.time()))
    daemon._on_switch_event(SwitchEvent("game_select", "pressed", time.time()))

    daemon._shader_controller.toggle_shader.assert_not_called()
    daemon._input_injector.press_key.assert_not_called()


def test_startup_sync_fires_key_for_active_toggle(tmp_config, monkeypatch):
    from retropie2600 import daemon as daemon_module

    mock_config = MagicMock()
    mock_config.shader = {"retroarch_host": "127.0.0.1", "retroarch_port": 55355}
    mock_config.shutdown = {"command": "sudo shutdown -h now", "delay_ms": 500}

    mock_monitor = MagicMock()
    mock_monitor.read_all_states.return_value = {"tv_type": "color"}
    mock_injector = MagicMock()
    mock_shutdown = MagicMock()
    mock_shutdown.is_shutting_down = False

    monkeypatch.setattr(daemon_module.Config, "from_file", MagicMock(return_value=mock_config))
    monkeypatch.setattr(daemon_module, "GPIOMonitor", MagicMock(return_value=mock_monitor))
    monkeypatch.setattr(daemon_module, "InputInjector", MagicMock(return_value=mock_injector))
    monkeypatch.setattr(daemon_module, "ShaderController", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(daemon_module, "ShutdownController", MagicMock(return_value=mock_shutdown))
    monkeypatch.setattr(daemon_module, "PowerLED", MagicMock(return_value=MagicMock()))

    daemon = _build_daemon(tmp_config)
    monkeypatch.setattr(daemon._shutdown_event, "wait", MagicMock(return_value=True))

    assert daemon.run() == 0
    mock_injector.press_key.assert_called_once_with("tv_type_color")


def test_sdnotify_fallback_when_import_fails(tmp_config, monkeypatch):
    import importlib

    real_import_module = importlib.import_module

    def _import_side_effect(name, package=None):
        if name == "sdnotify":
            raise ImportError("sdnotify not installed")
        return real_import_module(name, package)

    monkeypatch.setattr(importlib, "import_module", _import_side_effect)
    daemon_module = importlib.reload(importlib.import_module("retropie2600.daemon"))

    mock_config = MagicMock()
    mock_config.shader = {"retroarch_host": "127.0.0.1", "retroarch_port": 55355}
    mock_config.shutdown = {"command": "sudo shutdown -h now", "delay_ms": 500}
    monkeypatch.setattr(daemon_module.Config, "from_file", MagicMock(return_value=mock_config))

    mock_monitor = MagicMock()
    mock_monitor.read_all_states.return_value = {}
    monkeypatch.setattr(daemon_module, "GPIOMonitor", MagicMock(return_value=mock_monitor))
    monkeypatch.setattr(daemon_module, "InputInjector", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(daemon_module, "ShaderController", MagicMock(return_value=MagicMock()))
    mock_shutdown = MagicMock()
    mock_shutdown.is_shutting_down = False
    monkeypatch.setattr(daemon_module, "ShutdownController", MagicMock(return_value=mock_shutdown))
    monkeypatch.setattr(daemon_module, "PowerLED", MagicMock(return_value=MagicMock()))

    daemon = daemon_module.RetroPie2600Daemon(tmp_config)
    monkeypatch.setattr(daemon._shutdown_event, "wait", MagicMock(return_value=True))

    assert daemon.run() == 0
    importlib.reload(daemon_module)


def test_signal_handling_sigterm_sets_shutdown(tmp_config):
    daemon = _build_daemon(tmp_config)

    daemon._handle_signal(signal.SIGTERM, None)

    assert daemon._shutdown_event.is_set()


def test_cli_help_shows_config_and_log_level(capsys):
    from retropie2600.daemon import main

    try:
        main(["--help"])
        raise AssertionError("Expected SystemExit for --help")
    except SystemExit:
        pass

    captured = capsys.readouterr()
    assert "--config" in captured.out
    assert "--log-level" in captured.out


def test_shutdown_order_monitor_before_injector(tmp_config, monkeypatch):
    from retropie2600 import daemon as daemon_module

    mock_config = MagicMock()
    mock_config.shader = {"retroarch_host": "127.0.0.1", "retroarch_port": 55355}
    mock_config.shutdown = {"command": "sudo shutdown -h now", "delay_ms": 500}

    monkeypatch.setattr(daemon_module.Config, "from_file", MagicMock(return_value=mock_config))

    call_order = []
    mock_monitor = MagicMock()
    mock_monitor.read_all_states.return_value = {}
    mock_monitor.stop.side_effect = lambda: call_order.append("monitor_stop")

    mock_injector = MagicMock()
    mock_injector.close.side_effect = lambda: call_order.append("injector_close")

    mock_led = MagicMock()
    mock_led.off.side_effect = lambda: call_order.append("led_off")

    monkeypatch.setattr(daemon_module, "GPIOMonitor", MagicMock(return_value=mock_monitor))
    monkeypatch.setattr(daemon_module, "InputInjector", MagicMock(return_value=mock_injector))
    monkeypatch.setattr(daemon_module, "ShaderController", MagicMock(return_value=MagicMock()))
    mock_shutdown = MagicMock()
    mock_shutdown.is_shutting_down = False
    monkeypatch.setattr(daemon_module, "ShutdownController", MagicMock(return_value=mock_shutdown))
    monkeypatch.setattr(daemon_module, "PowerLED", MagicMock(return_value=mock_led))

    daemon = _build_daemon(tmp_config)
    monkeypatch.setattr(daemon._shutdown_event, "wait", MagicMock(return_value=True))

    assert daemon.run() == 0
    assert call_order == ["led_off", "monitor_stop", "injector_close"]


def test_power_led_on_after_ready_off_on_shutdown(tmp_config, monkeypatch):
    from retropie2600 import daemon as daemon_module

    mock_config = MagicMock()
    mock_config.shader = {"retroarch_host": "127.0.0.1", "retroarch_port": 55355}
    mock_config.shutdown = {"command": "sudo shutdown -h now", "delay_ms": 500}
    mock_config.power_led = {"pin": 12}

    mock_monitor = MagicMock()
    mock_monitor.read_all_states.return_value = {}

    mock_led = MagicMock()
    mock_shutdown = MagicMock()
    mock_shutdown.is_shutting_down = False

    monkeypatch.setattr(daemon_module.Config, "from_file", MagicMock(return_value=mock_config))
    monkeypatch.setattr(daemon_module, "GPIOMonitor", MagicMock(return_value=mock_monitor))
    monkeypatch.setattr(daemon_module, "InputInjector", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(daemon_module, "ShaderController", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(daemon_module, "ShutdownController", MagicMock(return_value=mock_shutdown))
    led_ctor = MagicMock(return_value=mock_led)
    monkeypatch.setattr(daemon_module, "PowerLED", led_ctor)

    daemon = _build_daemon(tmp_config)
    monkeypatch.setattr(daemon._shutdown_event, "wait", MagicMock(return_value=True))

    assert daemon.run() == 0

    led_ctor.assert_called_once_with(pin=12)
    mock_led.start.assert_called_once()
    mock_led.on.assert_called_once()
    mock_led.off.assert_called_once()

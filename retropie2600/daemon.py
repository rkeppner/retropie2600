from __future__ import annotations

import argparse
import importlib
import logging
import signal
import sys
import threading

from retropie2600.config import Config
from retropie2600.gpio_monitor import GPIOMonitor, SwitchEvent
from retropie2600.input_injector import InputInjector
from retropie2600.shader_controller import ShaderController
from retropie2600.shutdown_controller import ShutdownController

try:
    _sdnotify = importlib.import_module("sdnotify")
    _notifier = _sdnotify.SystemdNotifier()
except ImportError:
    class _NoOpNotifier:
        def notify(self, *a, **kw):
            return None

    _notifier = _NoOpNotifier()


logger = logging.getLogger(__name__)

_WATCHDOG_INTERVAL = 30


class RetroPie2600Daemon:
    def __init__(self, config_path: str) -> None:
        self._config_path = config_path
        self._gpio_monitor: GPIOMonitor | None = None
        self._input_injector: InputInjector | None = None
        self._shader_controller: ShaderController | None = None
        self._shutdown_controller: ShutdownController | None = None
        self._shutdown_event = threading.Event()

    def run(self) -> int:
        try:
            logger.info("Loading config from %s", self._config_path)
            config = Config.from_file(self._config_path)
        except Exception as exc:
            logger.error("Failed to load config: %s", exc)
            return 1

        try:
            self._input_injector = InputInjector()
            self._shader_controller = ShaderController(
                host=config.shader["retroarch_host"],
                port=config.shader["retroarch_port"],
            )
            self._shutdown_controller = ShutdownController(
                command=config.shutdown["command"],
                delay_ms=config.shutdown["delay_ms"],
            )
            self._gpio_monitor = GPIOMonitor(config=config, callback=self._on_switch_event)
        except Exception as exc:
            logger.error("Failed to initialize subsystems: %s", exc)
            return 1

        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

        self._gpio_monitor.start()

        startup_states = self._gpio_monitor.read_all_states()
        for switch_name, position in startup_states.items():
            key_name = f"{switch_name}_{position}"
            self._input_injector.press_key(key_name)

        _notifier.notify("READY=1")
        logger.info("retropie2600 daemon ready (config=%s)", self._config_path)

        while not self._shutdown_event.wait(timeout=_WATCHDOG_INTERVAL):
            _notifier.notify("WATCHDOG=1")

        if self._gpio_monitor is not None:
            self._gpio_monitor.stop()
        if self._input_injector is not None:
            self._input_injector.close()

        return 0

    def _on_switch_event(self, event: SwitchEvent) -> None:
        if (
            self._shutdown_controller is not None
            and self._shutdown_controller.is_shutting_down
        ):
            logger.info("Ignoring event during shutdown")
            return

        if event.switch_name == "power" and event.position == "off":
            if self._shutdown_controller is not None:
                self._shutdown_controller.initiate_shutdown()
            return

        if event.switch_name == "channel":
            if self._shader_controller is not None:
                self._shader_controller.toggle_shader()
            return

        if event.switch_name in {"game_select", "game_reset"}:
            if event.position == "pressed" and self._input_injector is not None:
                self._input_injector.press_key(event.switch_name)
            return

        if event.switch_name in {"tv_type", "difficulty_left", "difficulty_right"}:
            if self._input_injector is not None:
                key_name = f"{event.switch_name}_{event.position}"
                self._input_injector.press_key(key_name)
            return

        logger.warning(
            "Unknown switch event ignored: switch=%s position=%s",
            event.switch_name,
            event.position,
        )

    def _handle_signal(self, signum: int, frame) -> None:
        del frame
        logger.info("Received signal %d — shutting down", signum)
        self._shutdown_event.set()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="retropie2600 daemon — Atari 2600 switch GPIO daemon"
    )
    parser.add_argument(
        "--config",
        default="config/switches.yaml",
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    daemon = RetroPie2600Daemon(args.config)
    return daemon.run()


if __name__ == "__main__":
    sys.exit(main())

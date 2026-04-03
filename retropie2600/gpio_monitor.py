import logging
import time
from dataclasses import dataclass
from enum import Enum
from importlib import import_module
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    pigpio = import_module("pigpio")
except ImportError:
    pigpio = None

logger = logging.getLogger(__name__)

# pigpio set_glitch_filter maximum: 300000 µs (300 ms)
_MAX_GLITCH_FILTER_US = 300_000


class SwitchType(Enum):
    MOMENTARY = "momentary"
    TOGGLE = "toggle"


@dataclass
class SwitchEvent:
    switch_name: str
    position: str
    timestamp: float


class GPIOMonitor:
    def __init__(
        self,
        config: Any,
        callback: Callable[[SwitchEvent], None],
        pigpio_instance: Optional[Any] = None,
    ) -> None:
        self._config = config
        self._callback = callback
        self._pi = pigpio_instance
        self._callback_handles: List[Any] = []
        self._stub_mode = False

    def start(self) -> None:
        if pigpio is None:
            logger.warning("pigpio not available — running in stub mode (no GPIO monitoring)")
            self._stub_mode = True
            return

        if self._pi is None:
            self._pi = pigpio.pi()

        if not self._pi.connected:
            logger.warning("pigpiod not running — running in stub mode")
            self._stub_mode = True
            return

        self._stub_mode = False
        for switch_name, switch_cfg in self._config.switches.items():
            switch_type = SwitchType(switch_cfg.get("type", "toggle"))
            debounce_us = min(switch_cfg.get("debounce_ms", 20) * 1000, _MAX_GLITCH_FILTER_US)
            pins_for_switch = self._get_pins_for_switch(switch_name, switch_cfg)
            single_pin_positions = self._get_single_pin_toggle_positions(
                switch_name,
                switch_cfg,
                switch_type,
            )

            for pin, position_name in pins_for_switch:
                self._pi.set_mode(pin, pigpio.INPUT)
                self._pi.set_pull_up_down(pin, pigpio.PUD_UP)
                self._pi.set_glitch_filter(pin, debounce_us)
                positions = single_pin_positions if position_name == "single_pin_toggle" else None
                handle = self._pi.callback(
                    pin,
                    pigpio.EITHER_EDGE,
                    self._make_edge_handler(
                        switch_name,
                        position_name,
                        switch_type,
                        positions=positions,
                    ),
                )
                self._callback_handles.append(handle)

        logger.info("GPIO monitor started, %d callbacks registered", len(self._callback_handles))

    def stop(self) -> None:
        for handle in self._callback_handles:
            handle.cancel()
        self._callback_handles.clear()

        if self._pi and not self._stub_mode and pigpio is not None:
            self._pi.stop()

        logger.info("GPIO monitor stopped")

    def read_all_states(self) -> Dict[str, str]:
        if self._stub_mode or self._pi is None or not self._pi.connected:
            return {}

        states: Dict[str, str] = {}
        for switch_name, switch_cfg in self._config.switches.items():
            switch_type = SwitchType(switch_cfg.get("type", "toggle"))
            if switch_type != SwitchType.TOGGLE:
                continue

            single_pin_positions = self._get_single_pin_toggle_positions(
                switch_name,
                switch_cfg,
                switch_type,
            )
            if single_pin_positions is not None:
                level = self._pi.read(switch_cfg["pin"])
                states[switch_name] = (
                    single_pin_positions["low"] if level == 0 else single_pin_positions["high"]
                )
                continue

            pins = self._get_pins_for_switch(switch_name, switch_cfg)
            for pin, position_name in pins:
                level = self._pi.read(pin)
                if level == 0:
                    states[switch_name] = position_name
                    break

        return states

    def _get_single_pin_toggle_positions(
        self,
        switch_name: str,
        switch_cfg: dict,
        switch_type: SwitchType,
    ) -> Optional[Dict[str, str]]:
        if switch_type != SwitchType.TOGGLE:
            return None
        if "pin" not in switch_cfg or "positions" not in switch_cfg:
            return None

        positions = switch_cfg["positions"]
        if not isinstance(positions, dict):
            return None
        if "low" not in positions or "high" not in positions:
            return None

        return {"low": positions["low"], "high": positions["high"]}

    def _get_pins_for_switch(self, switch_name: str, switch_cfg: dict) -> List[Tuple[int, str]]:
        pins: List[Tuple[int, str]] = []
        switch_type = SwitchType(switch_cfg.get("type", "toggle"))
        single_pin_positions = self._get_single_pin_toggle_positions(
            switch_name,
            switch_cfg,
            switch_type,
        )
        if single_pin_positions is not None:
            return [(switch_cfg["pin"], "single_pin_toggle")]

        if "pin" in switch_cfg:
            pins.append((switch_cfg["pin"], "pressed"))
        if "pin_color" in switch_cfg:
            pins.append((switch_cfg["pin_color"], "color"))
        if "pin_bw" in switch_cfg:
            pins.append((switch_cfg["pin_bw"], "bw"))
        if "pin_a" in switch_cfg:
            pins.append((switch_cfg["pin_a"], "a"))
        if "pin_b" in switch_cfg:
            pins.append((switch_cfg["pin_b"], "b"))
        if "pin_2" in switch_cfg:
            pins.append((switch_cfg["pin_2"], "2"))
        if "pin_3" in switch_cfg:
            pins.append((switch_cfg["pin_3"], "3"))
        return pins

    def _make_edge_handler(
        self,
        switch_name: str,
        position_name: str,
        switch_type: SwitchType,
        positions: Optional[Dict[str, str]] = None,
    ) -> Callable[[int, int, int], None]:
        def _on_edge(gpio: int, level: int, tick: int) -> None:
            del gpio, tick

            if switch_type == SwitchType.MOMENTARY:
                actual_position = "pressed" if level == 0 else "released"
            else:
                if positions is not None:
                    actual_position = positions["low"] if level == 0 else positions["high"]
                else:
                    if level != 0:
                        return
                    actual_position = position_name

            event = SwitchEvent(
                switch_name=switch_name,
                position=actual_position,
                timestamp=time.time(),
            )
            logger.debug("Switch event: %s → %s", switch_name, actual_position)
            self._callback(event)

        return _on_edge

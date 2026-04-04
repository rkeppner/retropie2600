"""Power LED controller for retropie2600."""
from __future__ import annotations

import logging
from importlib import import_module
from typing import Any, Optional

try:
    pigpio = import_module("pigpio")
except ImportError:
    pigpio = None

logger = logging.getLogger(__name__)


class PowerLED:

    def __init__(
        self,
        pin: int,
        pigpio_instance: Optional[Any] = None,
    ) -> None:
        self._pin = pin
        self._pi = pigpio_instance
        self._stub_mode = False
        self._is_on = False

    def start(self) -> None:
        if pigpio is None:
            logger.warning("pigpio not available — power LED running in stub mode")
            self._stub_mode = True
            return

        if self._pi is None:
            self._pi = pigpio.pi()

        if not self._pi.connected:
            logger.warning("pigpiod not running — power LED running in stub mode")
            self._stub_mode = True
            return

        self._stub_mode = False
        self._pi.set_mode(self._pin, pigpio.OUTPUT)
        logger.info("Power LED initialised on BCM %d", self._pin)

    def on(self) -> None:
        if self._stub_mode or self._pi is None:
            self._is_on = True
            return
        self._pi.write(self._pin, 1)
        self._is_on = True
        logger.info("Power LED on")

    def off(self) -> None:
        if self._stub_mode or self._pi is None:
            self._is_on = False
            return
        self._pi.write(self._pin, 0)
        self._is_on = False
        logger.info("Power LED off")

    @property
    def is_on(self) -> bool:
        return self._is_on

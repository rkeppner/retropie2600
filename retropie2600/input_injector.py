"""Input injector for Stella keyboard events via Linux evdev/uinput.

Maps Atari 2600 switch events to Stella/RetroArch keyboard commands,
injected via the Linux uinput kernel interface.

Gracefully degrades on macOS where evdev is not available.
"""

import logging
import time
from typing import Dict, Optional

try:
    from evdev import UInput, ecodes
except ImportError:
    UInput = None
    ecodes = None

logger = logging.getLogger(__name__)

# Stella keyboard mapping: switch event identifier → evdev key code
# These F-key bindings are the default Stella mappings for 2600 console controls
STELLA_KEYS: Dict[str, int] = {}

# Only populate when evdev is available (avoids NameError at module level on macOS)
def _build_stella_keys() -> Dict[str, int]:
    if ecodes is None:
        # Return a string-based placeholder dict for documentation purposes
        # Real codes will be used when evdev is available
        return {
            "game_select": 59,        # KEY_F1
            "game_reset": 60,         # KEY_F2
            "tv_type_color": 61,      # KEY_F3
            "tv_type_bw": 62,         # KEY_F4
            "difficulty_left_a": 63,  # KEY_F5
            "difficulty_left_b": 64,  # KEY_F6
            "difficulty_right_a": 65, # KEY_F7
            "difficulty_right_b": 66, # KEY_F8
        }
    return {
        "game_select": ecodes.KEY_F1,
        "game_reset": ecodes.KEY_F2,
        "tv_type_color": ecodes.KEY_F3,
        "tv_type_bw": ecodes.KEY_F4,
        "difficulty_left_a": ecodes.KEY_F5,
        "difficulty_left_b": ecodes.KEY_F6,
        "difficulty_right_a": ecodes.KEY_F7,
        "difficulty_right_b": ecodes.KEY_F8,
    }

STELLA_KEYS = _build_stella_keys()

# evdev constants (fallback values when evdev not available)
_EV_KEY = 1  # ecodes.EV_KEY
_KEY_DOWN = 1
_KEY_UP = 0


class InputInjector:
    """Injects Stella keyboard events via Linux uinput virtual keyboard.

    Creates a virtual keyboard device that appears to the OS as a real
    keyboard, injecting F1-F8 keypresses to control the Stella emulator.

    Gracefully degrades on macOS where evdev/uinput is not available.

    Args:
        device_name: Name for the virtual keyboard device (default: "retropie2600-switches")
        uinput_instance: Optional pre-created UInput instance (for testing/injection)
    """

    def __init__(
        self,
        device_name: str = "retropie2600-switches",
        uinput_instance: Optional[object] = None,
    ):
        self._device_name = device_name
        self._stub_mode = False
        self._ui = uinput_instance

        if self._ui is not None:
            # Injected instance (for testing) — not stub mode
            return

        if UInput is None:
            logger.warning("evdev not available — running in stub mode (no key injection)")
            self._stub_mode = True
            return

        try:
            ev_key_code = ecodes.EV_KEY if ecodes else _EV_KEY
            registered_keys = list(STELLA_KEYS.values())
            self._ui = UInput(
                name=self._device_name,
                events={ev_key_code: registered_keys},
            )
            logger.info("InputInjector created virtual keyboard: %s", self._device_name)
        except Exception as e:
            logger.warning("Failed to create uinput device: %s — running in stub mode", e)
            self._stub_mode = True

    def press_key(self, key_name: str) -> None:
        """Send a keypress (down + up) for the given Stella key name.

        Args:
            key_name: Stella key identifier (e.g., "game_select", "tv_type_color")
        """
        if self._stub_mode or self._ui is None:
            return

        key_code = STELLA_KEYS.get(key_name)
        if key_code is None:
            logger.warning("Unknown Stella key: %r — ignoring", key_name)
            return

        ev_key = ecodes.EV_KEY if ecodes else _EV_KEY
        try:
            self._ui.write(ev_key, key_code, _KEY_DOWN)  # key down
            self._ui.syn()
            time.sleep(0.01)  # 10ms between down and up
            self._ui.write(ev_key, key_code, _KEY_UP)    # key up
            self._ui.syn()
            logger.debug("Injected key: %s (code %d)", key_name, key_code)
        except Exception as e:
            logger.error("Key injection failed for %r: %s", key_name, e)

    def close(self) -> None:
        """Close the uinput virtual keyboard device."""
        if self._ui is not None and not self._stub_mode:
            try:
                self._ui.close()
            except Exception as e:
                logger.warning("Error closing uinput device: %s", e)
        self._ui = None

"""Tests for retropie2600.input_injector module.

All tests run on macOS without evdev installed by using mock_evdev_uinput
fixture from conftest.py, injected via the uinput_instance parameter.
"""

import pytest
from unittest.mock import MagicMock, patch, call

from retropie2600.input_injector import STELLA_KEYS, InputInjector, _EV_KEY, _KEY_DOWN, _KEY_UP


EXPECTED_STELLA_KEYS = [
    "game_select",
    "game_reset",
    "tv_type_color",
    "tv_type_bw",
    "difficulty_left_a",
    "difficulty_left_b",
    "difficulty_right_a",
    "difficulty_right_b",
]


class TestStellaKeys:
    def test_stella_keys_has_all_8_mappings(self):
        """STELLA_KEYS contains exactly the 8 expected Atari 2600 switch names."""
        assert set(STELLA_KEYS.keys()) == set(EXPECTED_STELLA_KEYS)
        assert len(STELLA_KEYS) == 8

    def test_stella_key_values_are_integers(self):
        """All values in STELLA_KEYS are integers (evdev key codes)."""
        for key_name, key_code in STELLA_KEYS.items():
            assert isinstance(key_code, int), (
                f"STELLA_KEYS[{key_name!r}] should be int, got {type(key_code)}"
            )


class TestInputInjectorPressKey:
    def test_press_key_sends_key_down_syn_key_up_syn(self, mock_evdev_uinput):
        """press_key sends write(EV_KEY, code, 1), syn(), write(EV_KEY, code, 0), syn()."""
        injector = InputInjector(uinput_instance=mock_evdev_uinput)
        injector.press_key("game_select")

        expected_key_code = STELLA_KEYS["game_select"]

        assert mock_evdev_uinput.write.call_count == 2
        assert mock_evdev_uinput.syn.call_count == 2

        calls = mock_evdev_uinput.write.call_args_list
        assert calls[0] == call(_EV_KEY, expected_key_code, _KEY_DOWN)
        assert calls[1] == call(_EV_KEY, expected_key_code, _KEY_UP)

    def test_press_key_unknown_name_does_not_raise(self, mock_evdev_uinput):
        """press_key with unknown key name logs a warning but never raises."""
        injector = InputInjector(uinput_instance=mock_evdev_uinput)
        # Should not raise
        injector.press_key("nonexistent")
        # write() should never have been called
        mock_evdev_uinput.write.assert_not_called()

    def test_press_key_stub_mode_does_nothing(self):
        """In stub mode (UInput=None), press_key is a complete no-op."""
        with patch("retropie2600.input_injector.UInput", None):
            injector = InputInjector()
        assert injector._stub_mode is True
        # No mock to assert on, but this must not raise
        injector.press_key("game_select")

    def test_all_8_stella_keys_can_be_pressed(self, mock_evdev_uinput):
        """All 8 Stella keys can be pressed without exception."""
        injector = InputInjector(uinput_instance=mock_evdev_uinput)
        for key_name in EXPECTED_STELLA_KEYS:
            injector.press_key(key_name)

        # Each press_key makes 2 write() calls, so 8 keys = 16 total
        assert mock_evdev_uinput.write.call_count == 16
        assert mock_evdev_uinput.syn.call_count == 16


class TestInputInjectorClose:
    def test_close_calls_close_on_uinput(self, mock_evdev_uinput):
        """close() calls close() on the underlying uinput device."""
        injector = InputInjector(uinput_instance=mock_evdev_uinput)
        injector.close()
        mock_evdev_uinput.close.assert_called_once()
        assert injector._ui is None

    def test_close_idempotent_after_close(self, mock_evdev_uinput):
        """close() can be called multiple times without error."""
        injector = InputInjector(uinput_instance=mock_evdev_uinput)
        injector.close()
        # Second close should not raise even though _ui is None
        injector.close()


class TestInputInjectorInit:
    def test_stub_mode_when_uinput_unavailable(self):
        """InputInjector enters stub mode gracefully when UInput is None."""
        with patch("retropie2600.input_injector.UInput", None):
            injector = InputInjector()
        assert injector._stub_mode is True
        assert injector._ui is None

    def test_injected_uinput_not_stub_mode(self, mock_evdev_uinput):
        """When uinput_instance is injected, stub mode is False."""
        injector = InputInjector(uinput_instance=mock_evdev_uinput)
        assert injector._stub_mode is False
        assert injector._ui is mock_evdev_uinput

    def test_uinput_creation_failure_enters_stub_mode(self):
        """If UInput() constructor raises, InputInjector enters stub mode."""
        mock_uinput_cls = MagicMock(side_effect=PermissionError("no uinput access"))
        mock_ecodes = MagicMock()
        mock_ecodes.EV_KEY = 1
        with patch("retropie2600.input_injector.UInput", mock_uinput_cls):
            with patch("retropie2600.input_injector.ecodes", mock_ecodes):
                injector = InputInjector()
        assert injector._stub_mode is True

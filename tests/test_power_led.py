from types import SimpleNamespace
from unittest.mock import MagicMock

from retropie2600.power_led import PowerLED


def _mock_pigpio_module(mock_pi):
    return SimpleNamespace(
        OUTPUT=mock_pi.OUTPUT,
        pi=MagicMock(return_value=mock_pi),
    )


def _build_led(mock_pigpio, monkeypatch, pin=12):
    import retropie2600.power_led as led_module

    pigpio_module = _mock_pigpio_module(mock_pigpio)
    monkeypatch.setattr(led_module, "pigpio", pigpio_module)
    return PowerLED(pin=pin, pigpio_instance=mock_pigpio)


def test_start_configures_pin_as_output(mock_pigpio, monkeypatch):
    led = _build_led(mock_pigpio, monkeypatch)
    led.start()

    mock_pigpio.set_mode.assert_called_once_with(12, mock_pigpio.OUTPUT)


def test_on_writes_high(mock_pigpio, monkeypatch):
    led = _build_led(mock_pigpio, monkeypatch)
    led.start()
    led.on()

    mock_pigpio.write.assert_called_once_with(12, 1)
    assert led.is_on is True


def test_off_writes_low(mock_pigpio, monkeypatch):
    led = _build_led(mock_pigpio, monkeypatch)
    led.start()
    led.on()
    led.off()

    mock_pigpio.write.assert_called_with(12, 0)
    assert led.is_on is False


def test_on_off_cycle(mock_pigpio, monkeypatch):
    led = _build_led(mock_pigpio, monkeypatch)
    led.start()

    led.on()
    assert led.is_on is True
    led.off()
    assert led.is_on is False
    led.on()
    assert led.is_on is True


def test_stub_mode_when_pigpio_unavailable(monkeypatch):
    import retropie2600.power_led as led_module
    monkeypatch.setattr(led_module, "pigpio", None)

    led = PowerLED(pin=12)
    led.start()
    led.on()
    assert led.is_on is True
    led.off()
    assert led.is_on is False


def test_stub_mode_when_pigpiod_not_connected(monkeypatch):
    import retropie2600.power_led as led_module

    pi = MagicMock()
    pi.connected = False
    pigpio_module = SimpleNamespace(OUTPUT=1, pi=MagicMock(return_value=pi))
    monkeypatch.setattr(led_module, "pigpio", pigpio_module)

    led = PowerLED(pin=12, pigpio_instance=pi)
    led.start()
    led.on()

    pi.write.assert_not_called()
    assert led.is_on is True


def test_default_state_is_off():
    led = PowerLED(pin=12)
    assert led.is_on is False

"""YAML configuration loader and validator for retropie2600."""
import yaml
from typing import Dict, Any


RESERVED_BCM_PINS = {0, 1, 2, 3, 7, 8, 9, 10, 11, 14, 15}
VALID_BCM_RANGE = range(0, 28)


class ConfigError(ValueError):
    """Raised when configuration is invalid."""
    pass


class Config:
    """Configuration container for retropie2600 daemon."""
    
    def __init__(self, data: dict):
        self._data = data
        self._validate()
    
    @classmethod
    def from_file(cls, path: str) -> "Config":
        """Load and validate configuration from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        if not data:
            raise ConfigError(f"Config file {path!r} is empty")
        return cls(data)
    
    @property
    def switches(self) -> dict:
        return self._data["switches"]
    
    @property
    def shader(self) -> dict:
        return self._data.get("shader", {"retroarch_host": "127.0.0.1", "retroarch_port": 55355})
    
    @property
    def shutdown(self) -> dict:
        return self._data.get("shutdown", {"command": "sudo shutdown -h now", "delay_ms": 500})
    
    @property
    def power_led(self) -> dict:
        return self._data.get("power_led", {"pin": 12})
    
    @property
    def pin_assignments(self) -> Dict[str, Any]:
        """Return flat dict of logical_name → BCM pin number(s).
        
        Toggle switches with two positions return two entries:
          tv_type_color → 4, tv_type_bw → 17
        Single-pin switches return one entry:
          game_select → 22
        """
        result = {}
        for name, cfg in self.switches.items():
            if "pin" in cfg:
                result[name] = cfg["pin"]
            # tv_type: pin_color, pin_bw
            if "pin_color" in cfg:
                result[f"{name}_color"] = cfg["pin_color"]
            if "pin_bw" in cfg:
                result[f"{name}_bw"] = cfg["pin_bw"]
            # difficulty: pin_a, pin_b
            if "pin_a" in cfg:
                result[f"{name}_a"] = cfg["pin_a"]
            if "pin_b" in cfg:
                result[f"{name}_b"] = cfg["pin_b"]
            # channel: pin_2, pin_3
            if "pin_2" in cfg:
                result[f"{name}_2"] = cfg["pin_2"]
            if "pin_3" in cfg:
                result[f"{name}_3"] = cfg["pin_3"]
        return result
    
    @property
    def debounce_ms(self) -> Dict[str, int]:
        """Return dict of switch_name → debounce_ms value."""
        return {name: cfg.get("debounce_ms", 20) for name, cfg in self.switches.items()}
    
    def _validate(self):
        """Validate the loaded configuration."""
        if "switches" not in self._data:
            raise ConfigError("Missing required key 'switches'")
        
        # Collect all pins
        all_pins = []
        for name, cfg in self._data["switches"].items():
            for key, val in cfg.items():
                if "pin" in key and isinstance(val, int):
                    # Validate range
                    if val not in VALID_BCM_RANGE:
                        raise ConfigError(f"Switch '{name}' pin {key}={val} is out of valid BCM range 0-27")
                    # Validate not reserved
                    if val in RESERVED_BCM_PINS:
                        raise ConfigError(f"Switch '{name}' pin {key}={val} is a reserved BCM pin")
                    all_pins.append((name, key, val))
        
        # Check for duplicates
        seen_pins = {}
        for name, key, val in all_pins:
            if val in seen_pins:
                prev_name, prev_key = seen_pins[val]
                raise ConfigError(
                    f"Duplicate GPIO pin {val}: used by '{prev_name}.{prev_key}' and '{name}.{key}'"
                )
            seen_pins[val] = (name, key)

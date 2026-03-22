"""Tests for retropie2600.config module."""
import pytest
import tempfile
import os
from retropie2600.config import Config, ConfigError


class TestConfigLoading:
    """Test configuration file loading."""
    
    def test_config_loads_valid_file(self):
        """Test that a valid config file loads without error."""
        config = Config.from_file("config/switches.example.yaml")
        assert config is not None
        assert "power" in config.switches
        assert "game_select" in config.switches
    
    def test_empty_config_raises_error(self, tmp_path):
        """Test that an empty YAML file raises ConfigError."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")
        
        with pytest.raises(ConfigError):
            Config.from_file(str(yaml_file))


class TestPinAssignments:
    """Test pin_assignments property."""
    
    def test_pin_assignments_returns_correct_dict(self):
        """Test that pin_assignments returns expected switch→pin mappings."""
        config = Config.from_file("config/switches.example.yaml")
        assignments = config.pin_assignments
        
        # Single-pin switches
        assert assignments["power"] == 26
        assert assignments["game_select"] == 22
        assert assignments["game_reset"] == 27
        
        # Toggle switches with two pins
        assert assignments["tv_type_color"] == 4
        assert assignments["tv_type_bw"] == 17
        
        # Difficulty switches
        assert assignments["difficulty_left_a"] == 23
        assert assignments["difficulty_left_b"] == 24
        assert assignments["difficulty_right_a"] == 25
        assert assignments["difficulty_right_b"] == 5
        
        # Channel switch
        assert assignments["channel_2"] == 6
        assert assignments["channel_3"] == 13


class TestDebounce:
    """Test debounce_ms property."""
    
    def test_debounce_ms_returns_correct_dict(self):
        """Test that debounce_ms returns expected switch→debounce mappings."""
        config = Config.from_file("config/switches.example.yaml")
        debounce = config.debounce_ms
        
        assert debounce["power"] == 500
        assert debounce["tv_type"] == 20
        assert debounce["game_select"] == 5
        assert debounce["game_reset"] == 5
        assert debounce["difficulty_left"] == 20
        assert debounce["difficulty_right"] == 20
        assert debounce["channel"] == 20


class TestValidation:
    """Test configuration validation."""
    
    def test_missing_switches_key_raises_error(self, tmp_path):
        """Test that missing 'switches' key raises ConfigError."""
        yaml_file = tmp_path / "no_switches.yaml"
        yaml_file.write_text("""
shader:
  retroarch_host: "127.0.0.1"
  retroarch_port: 55355
""")
        
        with pytest.raises(ConfigError) as excinfo:
            Config.from_file(str(yaml_file))
        assert "switches" in str(excinfo.value)
    
    def test_duplicate_pin_raises_error(self, tmp_path):
        """Test that duplicate GPIO pins raise ConfigError."""
        yaml_file = tmp_path / "duplicate_pins.yaml"
        yaml_file.write_text("""
switches:
  game_select:
    pin: 22
    type: momentary
    debounce_ms: 5
  game_reset:
    pin: 22
    type: momentary
    debounce_ms: 5
""")
        
        with pytest.raises(ConfigError) as excinfo:
            Config.from_file(str(yaml_file))
        error_msg = str(excinfo.value)
        assert "Duplicate GPIO pin" in error_msg or "duplicate" in error_msg.lower()
        assert "22" in error_msg
    
    def test_invalid_pin_range_raises_error(self, tmp_path):
        """Test that out-of-range pin numbers raise ConfigError."""
        yaml_file = tmp_path / "invalid_pin.yaml"
        yaml_file.write_text("""
switches:
  game_select:
    pin: 99
    type: momentary
    debounce_ms: 5
""")
        
        with pytest.raises(ConfigError) as excinfo:
            Config.from_file(str(yaml_file))
        assert "out of valid BCM range" in str(excinfo.value)
    
    def test_reserved_pin_raises_error(self, tmp_path):
        """Test that reserved BCM pins raise ConfigError."""
        yaml_file = tmp_path / "reserved_pin.yaml"
        yaml_file.write_text("""
switches:
  game_select:
    pin: 14
    type: momentary
    debounce_ms: 5
""")
        
        with pytest.raises(ConfigError) as excinfo:
            Config.from_file(str(yaml_file))
        assert "reserved" in str(excinfo.value).lower()


class TestDefaults:
    """Test property defaults."""
    
    def test_shader_defaults(self, tmp_path):
        """Test that shader property returns defaults when not in config."""
        yaml_file = tmp_path / "no_shader.yaml"
        yaml_file.write_text("""
switches:
  game_select:
    pin: 22
    type: momentary
    debounce_ms: 5
""")
        
        config = Config.from_file(str(yaml_file))
        shader = config.shader
        
        assert shader["retroarch_host"] == "127.0.0.1"
        assert shader["retroarch_port"] == 55355
    
    def test_shutdown_defaults(self, tmp_path):
        """Test that shutdown property returns defaults when not in config."""
        yaml_file = tmp_path / "no_shutdown.yaml"
        yaml_file.write_text("""
switches:
  game_select:
    pin: 22
    type: momentary
    debounce_ms: 5
""")
        
        config = Config.from_file(str(yaml_file))
        shutdown = config.shutdown
        
        assert shutdown["command"] == "sudo shutdown -h now"
        assert shutdown["delay_ms"] == 500

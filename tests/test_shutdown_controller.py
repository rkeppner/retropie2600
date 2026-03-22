"""Test suite for shutdown controller."""

import pytest
import sys
import time
from unittest.mock import patch, MagicMock, ANY
from retropie2600.shutdown_controller import ShutdownController


def test_is_shutting_down_false_initially():
    """Fresh instance has is_shutting_down=False."""
    controller = ShutdownController()
    assert controller.is_shutting_down is False


def test_initiate_shutdown_sets_flag():
    """After initiate_shutdown(), is_shutting_down is True."""
    controller = ShutdownController(delay_ms=0)
    controller.initiate_shutdown()
    assert controller.is_shutting_down is True


def test_initiate_shutdown_runs_in_thread(monkeypatch):
    """Verify is_shutting_down=True immediately after call (not waiting for thread)."""
    with patch("retropie2600.shutdown_controller.subprocess.run") as mock_run:
        monkeypatch.setattr(sys, "platform", "linux")
        controller = ShutdownController(delay_ms=0)
        controller.initiate_shutdown()
        # Flag should be set immediately
        assert controller.is_shutting_down is True
        # Give the thread time to run
        time.sleep(0.05)
        # Subprocess should have been called
        mock_run.assert_called_once()


def test_double_call_protection(monkeypatch):
    """Call initiate_shutdown() twice, subprocess.run called at most once."""
    with patch("retropie2600.shutdown_controller.subprocess.run") as mock_run:
        monkeypatch.setattr(sys, "platform", "linux")
        controller = ShutdownController(delay_ms=0)
        controller.initiate_shutdown()
        controller.initiate_shutdown()  # Second call
        
        # Wait for thread
        time.sleep(0.05)
        
        # Should only be called once
        assert mock_run.call_count <= 1


def test_custom_shutdown_command(monkeypatch):
    """ShutdownController(command="sudo poweroff"), verify command passed correctly."""
    with patch("retropie2600.shutdown_controller.subprocess.run") as mock_run:
        monkeypatch.setattr(sys, "platform", "linux")
        controller = ShutdownController(command="sudo poweroff", delay_ms=0)
        controller.initiate_shutdown()
        
        # Wait for thread
        time.sleep(0.05)
        
        mock_run.assert_called_once_with(["sudo", "poweroff"], check=False)


def test_shutdown_skipped_on_macos(monkeypatch):
    """Patch sys.platform="darwin", subprocess.run NOT called."""
    with patch("retropie2600.shutdown_controller.subprocess.run") as mock_run:
        monkeypatch.setattr(sys, "platform", "darwin")
        
        controller = ShutdownController(delay_ms=0)
        controller.initiate_shutdown()
        
        # Wait for thread
        time.sleep(0.05)
        
        # subprocess.run should NOT have been called on macOS
        mock_run.assert_not_called()


def test_delay_ms_respected(monkeypatch):
    """ShutdownController(delay_ms=0), shutdown runs without delay."""
    with patch("retropie2600.shutdown_controller.subprocess.run") as mock_run:
        monkeypatch.setattr(sys, "platform", "linux")
        controller = ShutdownController(command="sudo shutdown -h now", delay_ms=0)
        
        start = time.time()
        controller.initiate_shutdown()
        time.sleep(0.05)  # Brief wait for thread
        elapsed = time.time() - start
        
        # Should run quickly (no 500ms delay)
        assert elapsed < 0.2
        mock_run.assert_called_once()


def test_shutdown_command_split_correctly(monkeypatch):
    """Verify command is split into list correctly."""
    with patch("retropie2600.shutdown_controller.subprocess.run") as mock_run:
        monkeypatch.setattr(sys, "platform", "linux")
        controller = ShutdownController(command="sudo shutdown -h now", delay_ms=0)
        controller.initiate_shutdown()
        
        time.sleep(0.05)
        
        # The command should be split into ["sudo", "shutdown", "-h", "now"]
        mock_run.assert_called_once_with(["sudo", "shutdown", "-h", "now"], check=False)

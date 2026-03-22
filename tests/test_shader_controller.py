"""Tests for ShaderController UDP network command interface."""

import pytest
from unittest.mock import MagicMock
from retropie2600.shader_controller import ShaderController, SHADER_TOGGLE_CMD


class TestToggleShaderSendsCorrectUDPPacket:
    """Test that toggle_shader() sends the correct UDP packet."""
    
    def test_toggle_shader_sends_correct_udp_packet(self, mock_socket):
        """toggle_shader() calls sendto with (b"SHADER_TOGGLE", ("127.0.0.1", 55355))."""
        controller = ShaderController(socket_instance=mock_socket)
        controller.toggle_shader()
        
        mock_socket.sendto.assert_called_once_with(
            b"SHADER_TOGGLE",
            ("127.0.0.1", 55355),
        )


class TestSendCommandSendsArbitraryCommand:
    """Test that send_command() sends arbitrary RetroArch commands."""
    
    def test_send_command_sends_arbitrary_command(self, mock_socket):
        """send_command("PAUSE_TOGGLE") sends b"PAUSE_TOGGLE"."""
        controller = ShaderController(socket_instance=mock_socket)
        controller.send_command("PAUSE_TOGGLE")
        
        mock_socket.sendto.assert_called_once_with(
            b"PAUSE_TOGGLE",
            ("127.0.0.1", 55355),
        )


class TestCustomHostAndPort:
    """Test that custom host and port are used correctly."""
    
    def test_custom_host_and_port(self, mock_socket):
        """ShaderController("192.168.1.1", 12345), toggle_shader() sends to correct address."""
        controller = ShaderController(
            host="192.168.1.1",
            port=12345,
            socket_instance=mock_socket,
        )
        controller.toggle_shader()
        
        mock_socket.sendto.assert_called_once_with(
            b"SHADER_TOGGLE",
            ("192.168.1.1", 12345),
        )


class TestSocketErrorIsCaughtAndNotRaised:
    """Test that socket errors are caught and logged, not raised."""
    
    def test_socket_error_is_caught_and_not_raised(self, mock_socket):
        """make mock_socket.sendto raise OSError, call toggle_shader(), assert no exception propagates."""
        mock_socket.sendto.side_effect = OSError("Connection refused")
        controller = ShaderController(socket_instance=mock_socket)
        
        # Should not raise
        controller.toggle_shader()
        
        # But sendto was still called
        mock_socket.sendto.assert_called_once_with(
            b"SHADER_TOGGLE",
            ("127.0.0.1", 55355),
        )


class TestSendCommandEncodesToBytes:
    """Test that send_command encodes string to bytes."""
    
    def test_send_command_encodes_to_bytes(self, mock_socket):
        """verify sendto receives bytes (b"SHADER_TOGGLE"), not string."""
        controller = ShaderController(socket_instance=mock_socket)
        controller.send_command("SHADER_TOGGLE")
        
        # Get the call args
        call_args = mock_socket.sendto.call_args
        data_arg = call_args[0][0]  # First positional argument
        
        # Assert it's bytes, not string
        assert isinstance(data_arg, bytes)
        assert data_arg == b"SHADER_TOGGLE"


class TestDefaultHostAndPort:
    """Test default host and port values."""
    
    def test_default_host_is_localhost(self, mock_socket):
        """Default host should be 127.0.0.1."""
        controller = ShaderController(socket_instance=mock_socket)
        controller.toggle_shader()
        
        call_args = mock_socket.sendto.call_args
        host, port = call_args[0][1]  # Second positional argument
        
        assert host == "127.0.0.1"
    
    def test_default_port_is_55355(self, mock_socket):
        """Default port should be 55355 (RetroArch default)."""
        controller = ShaderController(socket_instance=mock_socket)
        controller.toggle_shader()
        
        call_args = mock_socket.sendto.call_args
        host, port = call_args[0][1]  # Second positional argument
        
        assert port == 55355


class TestMultipleCommands:
    """Test sending multiple commands in sequence."""
    
    def test_multiple_commands_are_sent(self, mock_socket):
        """Multiple send_command calls should all be sent."""
        controller = ShaderController(socket_instance=mock_socket)
        
        controller.send_command("SHADER_TOGGLE")
        controller.send_command("PAUSE_TOGGLE")
        controller.send_command("SHADER_TOGGLE")
        
        assert mock_socket.sendto.call_count == 3
        
        calls = mock_socket.sendto.call_args_list
        assert calls[0][0][0] == b"SHADER_TOGGLE"
        assert calls[1][0][0] == b"PAUSE_TOGGLE"
        assert calls[2][0][0] == b"SHADER_TOGGLE"

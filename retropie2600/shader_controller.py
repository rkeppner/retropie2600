"""Shader controller for RetroArch UDP network command interface.

Sends shader toggle commands to RetroArch via UDP network commands.
RetroArch must have network_cmd_enable = "true" in retroarch.cfg.
"""

import logging
import socket
from typing import Optional

logger = logging.getLogger(__name__)

# RetroArch network command for shader toggle
SHADER_TOGGLE_CMD = "SHADER_TOGGLE"


class ShaderController:
    """Controls RetroArch CRT shader via UDP network commands.
    
    Sends SHADER_TOGGLE to RetroArch's network command interface.
    Fire-and-forget UDP — no response expected or required.
    
    Args:
        host: RetroArch network command host (default: "127.0.0.1")
        port: RetroArch network command port (default: 55355)
        socket_instance: Optional pre-created socket (for testing)
    """
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 55355,
        socket_instance: Optional[socket.socket] = None,
    ):
        self._host = host
        self._port = port
        self._socket = socket_instance  # injected for testing
    
    def toggle_shader(self) -> None:
        """Send SHADER_TOGGLE command to RetroArch via UDP."""
        self.send_command(SHADER_TOGGLE_CMD)
    
    def send_command(self, command: str) -> None:
        """Send an arbitrary RetroArch network command via UDP.
        
        Args:
            command: RetroArch network command string (e.g., "SHADER_TOGGLE", "PAUSE_TOGGLE")
        """
        try:
            if self._socket is not None:
                # Use injected socket (for testing)
                self._socket.sendto(command.encode("utf-8"), (self._host, self._port))
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.sendto(command.encode("utf-8"), (self._host, self._port))
            logger.debug("Sent RetroArch command: %s → %s:%d", command, self._host, self._port)
        except OSError as e:
            logger.error("Failed to send RetroArch command %r: %s", command, e)

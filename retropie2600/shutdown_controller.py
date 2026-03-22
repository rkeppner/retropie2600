"""Shutdown controller for safe Raspberry Pi power-off sequence.

Handles power switch events by executing a safe system shutdown,
with double-call protection to prevent repeated shutdown attempts.
"""

import logging
import subprocess
import sys
import time
from threading import Thread
from typing import Optional

logger = logging.getLogger(__name__)


class ShutdownController:
    """Manages safe system shutdown when power switch is triggered.
    
    Executes the configured shutdown command with an optional debounce delay.
    Protects against double-call via internal flag.
    
    On macOS/non-Pi platforms, logs "Shutdown skipped" instead of executing.
    
    Args:
        command: Shell command for system shutdown (default: "sudo shutdown -h now")
        delay_ms: Debounce delay in milliseconds before executing shutdown (default: 500)
    """
    
    def __init__(
        self,
        command: str = "sudo shutdown -h now",
        delay_ms: int = 500,
    ):
        self._command = command
        self._delay_ms = delay_ms
        self._shutting_down = False
    
    @property
    def is_shutting_down(self) -> bool:
        """True if shutdown has been initiated."""
        return self._shutting_down
    
    def initiate_shutdown(self) -> None:
        """Trigger safe system shutdown.
        
        If already shutting down, this call is silently ignored.
        Applies debounce delay before executing the shutdown command.
        On macOS, logs "Shutdown skipped" instead of running the command.
        """
        if self._shutting_down:
            logger.debug("Shutdown already in progress — ignoring duplicate trigger")
            return
        
        self._shutting_down = True
        logger.warning(
            "Safe shutdown initiated — system will halt after %dms delay",
            self._delay_ms,
        )
        
        # Run shutdown in a daemon thread to allow main loop to continue briefly
        thread = Thread(target=self._do_shutdown, daemon=True)
        thread.start()
    
    def _do_shutdown(self) -> None:
        """Execute the shutdown sequence (runs in background thread)."""
        if self._delay_ms > 0:
            time.sleep(self._delay_ms / 1000.0)
        
        # Platform check: only run actual shutdown on Linux
        if sys.platform != "linux":
            logger.info("Shutdown skipped (not on Linux/Pi platform): %s", self._command)
            return
        
        cmd_parts = self._command.split()
        logger.info("Executing shutdown: %s", self._command)
        subprocess.run(cmd_parts, check=False)

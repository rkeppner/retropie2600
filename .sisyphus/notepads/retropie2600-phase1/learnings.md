## 2026-03-22

- `GPIOMonitor` can stay fully hardware-agnostic in tests by injecting a mocked `pigpio_instance` and monkeypatching module-level `pigpio` constants/API.
- Toggle switch monitoring should register `EITHER_EDGE` but emit events only on `level == 0` to avoid duplicate state notifications.
- `read_all_states()` startup sync is reliable when it scans only toggle switches and maps active-low pins to semantic position names.

- Daemon startup sequence now mirrors rfid-vcr structure: load config, build subsystems, register SIGTERM/SIGINT handlers, start monitor, run startup toggle sync, then enter watchdog loop until shutdown event.
- Event routing contract in daemon is explicit and centralized: power/off triggers shutdown, channel triggers shader toggle, momentary switches fire only on pressed, and toggle switches map to key names as switch_position.
- sdnotify integration is importlib-based with a no-op notifier fallback, allowing macOS/dev test execution without Linux-only dependency installation.
- Shutdown teardown order is enforced and tested: GPIOMonitor.stop() executes before InputInjector.close() for predictable resource cleanup.

## 2026-03-22

- Implemented GPIO detection with pigpio callbacks (interrupt-driven) instead of polling to meet latency and architecture requirements.
- Added stub degradation paths for both `pigpio` import failure and disconnected `pigpiod` to keep local/macOS development safe and non-crashing.
- Kept `GPIOMonitor` focused on emitting typed `SwitchEvent` objects only, with no action dispatching, to preserve separation of concerns.

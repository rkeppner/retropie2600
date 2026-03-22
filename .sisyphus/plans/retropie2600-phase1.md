# RetroPie2600 Phase 1: Core Console Build

## TL;DR

> **Quick Summary**: Build a fully functional Atari 2600 console powered by a Raspberry Pi 3B+ running RetroPie, with all original switches wired to GPIO and mapped to emulator controls via a custom Python daemon, plus comprehensive hardware documentation.
> 
> **Deliverables**:
> - Custom Python daemon (`retropie2600`) that maps GPIO switch events to Stella/RetroArch controls
> - Hardware wiring guide with GPIO pinout, switch connections, power LED, and fan installation
> - RetroPie/RetroArch/lr-stella configuration files
> - systemd service for daemon auto-start
> - Installation and deployment documentation
> - Full pytest suite with mocked hardware (runs on macOS)
> 
> **Estimated Effort**: Medium-Large
> **Parallel Execution**: YES — 4 waves
> **Critical Path**: Task 1 → Task 2 → Task 3 → Tasks 4-6 (parallel) → Task 7 → Tasks 8-10 (parallel) → Task 11 → F1-F4

---

## Context

### Original Request
User wants to integrate a Raspberry Pi 3B+ into a vintage Atari 2600 CX-2600A (heavy sixer) shell, with original console switches wired to GPIO pins and mapped to lr-stella/RetroArch emulator controls. The system uses 2600-daptor 2e USB adapters for authentic joystick/paddle input. Phase 1 covers the core console build — hardware integration and software daemon. Phase 2 (future) will add cartridge ROM reading and auto-launch.

### Interview Summary
**Key Discussions**:
- **Switches**: All 6 original switches mapped via custom Python daemon. Toggle switches (TV Type, Difficulty L/R) need 2 GPIO pins each (one per position). Momentary switches (Select, Reset) need 1 pin each. Power switch triggers safe shutdown. Channel switch repurposed as CRT shader toggle.
- **Power**: Standard Pi micro-USB power supply through Dremel-cut hole. NO buck converter. Original power jack hole repurposed for red LED power indicator.
- **Power switch**: Software-only shutdown via `dtoverlay=gpio-shutdown` — flip OFF = safe shutdown, flip ON = wake from halt.
- **Emulator**: lr-stella (RetroArch core) for CRT shader integration.
- **CRT shader toggle**: Channel switch triggers RetroArch shader toggle via UDP network command (port 55355).
- **Development**: macOS development with graceful degradation stubs, deploy to Pi.
- **Testing**: pytest with mocked hardware interfaces — all tests run on macOS without Pi hardware.
- **Wiring**: Keep original Atari board (ICs removed), solder to pad traces, DuPont connectors on Pi GPIO end.
- **Cooling**: Active 5V fan with heatsink.
- **Video/Audio**: HDMI through Dremel-cut hole, audio via HDMI or 3.5mm jack (external only).
- **UI**: EmulationStation as primary interface. Cartridge auto-launch deferred to Phase 2.

**Research Findings**:
- Switch types confirmed: DPDT wired as SPST (toggles), DPDT momentary (Select/Reset), SPDT (Channel)
- Stella keyboard mappings: F1 (Select), F2 (Reset), F3/F4 (Color/BW), F5/F6 (Left Diff A/B), F7/F8 (Right Diff A/B)
- pigpio preferred over gpiozero/RPi.GPIO — hardware-timed edge detection, `set_glitch_filter()`, C daemon, lowest CPU
- python-evdev for uinput keyboard injection — works at Linux input layer, compatible with framebuffer/KMS mode
- RetroArch UDP network command interface for shader toggle (`SHADER_TOGGLE` on port 55355)
- RFID-VCR project (`/Users/rkeppner/Code/rfid-vcr/`) provides proven daemon architecture pattern
- rpie2600 by etheling is a similar project using PetrockBlock ControlBlock
- GPIO pin budget: ~10 pins for switches + 1 for power LED + 1 for fan control = ~12 of 26 available

### Metis Review
**Identified Gaps** (addressed):
- Power switch can't simultaneously cut power AND signal GPIO — resolved: software-only shutdown with gpio-shutdown overlay
- D24V50F5 is fixed 5.0V not adjustable — resolved: not using buck converter, standard Pi PSU instead
- Toggle initial state at startup — resolved: daemon reads and syncs all toggle states at boot
- pigpiod dependency — resolved: systemd `After=pigpiod.service` + `Requires=pigpiod.service`
- RetroArch not running when switch toggled — resolved: log and discard, stateless approach
- Shutdown race condition — resolved: daemon sets "shutting_down" flag, ignores subsequent switch events

---

## Work Objectives

### Core Objective
Create a custom Python daemon that reads Atari 2600 console switch positions via Raspberry Pi GPIO and maps them to lr-stella/RetroArch emulator controls, with comprehensive hardware documentation for physical assembly.

### Concrete Deliverables
- Python package `retropie2600/` with 6 modules: config, gpio_monitor, input_injector, shader_controller, shutdown_controller, daemon
- Config file `config/switches.example.yaml` with all pin assignments and settings
- systemd service unit `systemd/retropie2600.service`
- Hardware guide `docs/hardware-guide.md` with wiring diagrams, BOM, safety warnings
- Installation guide `docs/installation.md` with step-by-step RetroPie setup
- RetroArch/lr-stella config examples `config/retroarch.cfg.example`
- Full test suite `tests/` with mocked hardware — runs on macOS
- `conftest.py` with shared fixtures for mocked pigpio, evdev, socket

### Definition of Done
- [ ] `pytest tests/ -v` passes with 0 failures on macOS (no Pi hardware required)
- [ ] `python -m retropie2600.daemon --help` prints usage with `--config` and `--log-level` options
- [ ] All modules importable: `python -c "from retropie2600 import config, gpio_monitor, input_injector, shader_controller, shutdown_controller, daemon"`
- [ ] Config loads and validates: `python -c "from retropie2600.config import Config; c = Config.from_file('config/switches.example.yaml'); print(c.pin_assignments)"`
- [ ] systemd unit syntax valid: `systemd-analyze verify systemd/retropie2600.service` (on Linux)
- [ ] Hardware guide covers all 7 switches + power LED + fan with BCM pin numbers
- [ ] All BCM pin references in docs match config defaults

### Must Have
- All 6 original switches functional and mapped to correct Stella/RetroArch controls
- Power switch triggers safe shutdown via GPIO
- Channel switch toggles CRT shader via RetroArch UDP
- Power LED in original power jack hole
- Active fan cooling
- Configurable GPIO pin assignments (YAML, not hardcoded)
- Configurable debounce timing per switch type
- Graceful degradation stubs for macOS development
- Startup state sync — daemon reads toggle positions at boot and sends initial key events
- systemd service with sdnotify and watchdog

### Must NOT Have (Guardrails)
- ❌ No cartridge detection, ROM reading, GPIO expanders, level shifters, auto-launch (Phase 2)
- ❌ No CartridgeMonitor, CartridgeReader, ROMHasher classes
- ❌ No abstract base classes for "future extensibility"
- ❌ No plugin architecture or dynamic module loading
- ❌ No REST API, web interface, or GUI configuration tool
- ❌ No database — YAML config is sufficient
- ❌ No Docker/container support — bare metal Pi
- ❌ No multi-console support or "generic emulator framework"
- ❌ No gpiozero or RPi.GPIO — use pigpio only
- ❌ No xdotool — use python-evdev uinput only
- ❌ No hardcoded GPIO pin numbers in Python code
- ❌ No over-engineered error recovery beyond retry/log/continue
- ❌ No metrics, Prometheus endpoints, or health check APIs
- ❌ No LED status beyond the single power LED

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO (greenfield project)
- **Automated tests**: YES (TDD with pytest)
- **Framework**: pytest
- **Approach**: Each module developed with tests. Hardware interfaces mocked. All tests run on macOS.

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Python modules**: Use Bash — `pytest tests/test_X.py -v`, `python -c "import ..."`, `python -m retropie2600.daemon --help`
- **Config files**: Use Bash — load and validate with Python one-liners
- **Documentation**: Use Bash — verify file exists, check for required sections with grep
- **systemd units**: Use Bash — `systemd-analyze verify` (Linux only, skip on macOS)

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation):
├── Task 1: Project scaffolding + package structure + dev dependencies [quick]
├── Task 2: Configuration module with YAML loading and validation [quick]
└── Task 3: Test infrastructure — conftest.py with shared fixtures [quick]

Wave 2 (After Wave 1 — core modules, MAX PARALLEL):
├── Task 4: GPIO monitor with pigpio edge detection and switch events [deep]
├── Task 5: Input injector for Stella keyboard events via evdev/uinput [unspecified-high]
├── Task 6: Shader controller for RetroArch UDP commands [quick]
└── Task 7: Shutdown controller for safe power-off sequence [quick]

Wave 3 (After Wave 2 — integration + deployment):
├── Task 8: Main daemon with systemd integration and startup sync [deep]
├── Task 9: systemd service unit and udev rules [quick]
└── Task 10: RetroArch and lr-stella configuration files [quick]

Wave 4 (After Wave 3 — documentation):
├── Task 11: Hardware wiring guide with GPIO pinout and power circuit [writing]
└── Task 12: Complete installation guide for RetroPie setup [writing]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real QA — run full test suite + verify imports + validate configs (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 2, 3, 4, 5, 6, 7, 8, 9, 10 | 1 |
| 2 | 1 | 4, 5, 6, 7, 8 | 1 |
| 3 | 1 | 4, 5, 6, 7, 8 | 1 |
| 4 | 2, 3 | 8 | 2 |
| 5 | 2, 3 | 8 | 2 |
| 6 | 2, 3 | 8 | 2 |
| 7 | 2, 3 | 8 | 2 |
| 8 | 4, 5, 6, 7 | 9 | 3 |
| 9 | 8 | — | 3 |
| 10 | 1 | — | 3 |
| 11 | — | — | 4 |
| 12 | 9, 10 | — | 4 |
| F1-F4 | ALL | — | FINAL |

### Agent Dispatch Summary

- **Wave 1**: **3 tasks** — T1 → `quick`, T2 → `quick`, T3 → `quick`
- **Wave 2**: **4 tasks** — T4 → `deep`, T5 → `unspecified-high`, T6 → `quick`, T7 → `quick`
- **Wave 3**: **3 tasks** — T8 → `deep`, T9 → `quick`, T10 → `quick`
- **Wave 4**: **2 tasks** — T11 → `writing`, T12 → `writing`
- **FINAL**: **4 tasks** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [ ] 1. Project Scaffolding — Package Structure and Dev Dependencies

  **What to do**:
  - Create `pyproject.toml` with project metadata, Python ≥3.9 requirement:
    - Core dependencies: `pyyaml`
    - Platform-specific dependencies using PEP 508 markers: `pigpio; sys_platform == "linux"`, `evdev; sys_platform == "linux"`, `sdnotify; sys_platform == "linux"`
    - Dev dependencies (extras `[dev]`): `pytest`, `pytest-mock`
    - This ensures `pip install -e ".[dev]"` works on macOS (only installs pyyaml + test deps) AND on Pi (installs everything)
  - Create package directory `retropie2600/` with `__init__.py` (version string, brief docstring)
  - Create `tests/` directory with empty `__init__.py`
  - Create `.gitignore` with Python defaults (`.venv/`, `__pycache__/`, `*.pyc`, `.eggs/`, `dist/`, `*.egg-info/`, `.sisyphus/evidence/`)
  - Create `config/` directory (empty for now — will hold example configs)
  - Create `docs/` directory (empty for now — will hold guides)
  - Create `systemd/` directory (empty for now — will hold service files)
  - Verify: `pytest` runs with 0 tests collected, no errors

  **Must NOT do**:
  - ⛔ Do NOT create any Phase 2 files (cartridge-related modules)
  - ⛔ Do NOT add abstract base classes or plugin infrastructure
  - ⛔ Do NOT add gpiozero or RPi.GPIO as dependencies

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple scaffolding — creating directories and a pyproject.toml
  - **Skills**: []
    - No specialized skills needed for scaffolding

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (sequential — must complete first)
  - **Blocks**: Tasks 2, 3, 4, 5, 6, 7, 8, 9, 10
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/requirements.txt` — Reference for Pi-specific Python dependencies (pirc522, gpiozero, sdnotify, plexapi, pyyaml). Our equivalent: pigpio, evdev, sdnotify (all Linux-only via PEP 508 markers), pyyaml (cross-platform).
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/__init__.py` — Package init pattern to follow

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Project structure exists and pytest runs
    Tool: Bash
    Preconditions: Fresh clone of repository
    Steps:
      1. Run: ls retropie2600/__init__.py tests/__init__.py pyproject.toml .gitignore
      2. Assert: all 4 files exist (exit code 0)
      3. Run: ls config/ docs/ systemd/
      4. Assert: all 3 directories exist
      5. Run: pip install -e ".[dev]" (or pip install -e . with dev extras)
      6. Run: pytest --co
      7. Assert: exit code 0, output contains "no tests ran" or "0 items collected"
    Expected Result: All files/dirs exist, pytest runs without error
    Failure Indicators: Missing files, pytest import errors, dependency installation failure
    Evidence: .sisyphus/evidence/task-1-scaffolding-pytest.txt

  Scenario: Dependencies are correctly specified
    Tool: Bash
    Preconditions: Package installed in editable mode
    Steps:
      1. Run: python -c "import yaml; print(yaml.__version__)"
      2. Assert: prints version number without error
      3. Run: python -c "import pytest; print(pytest.__version__)"
      4. Assert: prints version number without error
      5. Run: python -c "from retropie2600 import __version__; print(__version__)"
      6. Assert: prints version string
    Expected Result: All imports succeed
    Evidence: .sisyphus/evidence/task-1-dependencies.txt
  ```

  **Commit**: YES
  - Message: `feat: add project scaffolding with package structure and dev deps`
  - Files: `pyproject.toml`, `retropie2600/__init__.py`, `tests/__init__.py`, `.gitignore`
  - Pre-commit: `pytest --co`

- [ ] 2. Configuration Module — YAML Loading, Validation, and Pin Assignments

  **What to do**:
  - Create `retropie2600/config.py` following the pattern from `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/config.py`:
    - `Config` dataclass/class with `from_file(path)` classmethod
    - Load YAML config file with `pyyaml`
    - Validate required keys: `switches` (with sub-keys for each switch), `debounce`, `shader`, `shutdown`
    - `pin_assignments` property returning dict of switch_name → BCM pin number(s)
    - `debounce_ms` property returning dict of switch_name → debounce value in ms
    - Validate no duplicate GPIO pin numbers across all switch assignments
    - Validate all BCM pin numbers are in valid range (0-27) and not in reserved set (0, 1, 2, 3, 7, 8, 9, 10, 11, 14, 15)
  - Create `config/switches.example.yaml` with all pin assignments and sensible defaults:
    ```yaml
    switches:
      power:
        pin: 26
        type: toggle  # software-only shutdown trigger
        debounce_ms: 500
      tv_type:
        pin_color: 4    # F3
        pin_bw: 17      # F4
        type: toggle
        debounce_ms: 20
      game_select:
        pin: 22         # F1
        type: momentary
        debounce_ms: 5
      game_reset:
        pin: 27         # F2
        type: momentary
        debounce_ms: 5
      difficulty_left:
        pin_a: 23       # F5
        pin_b: 24       # F6
        type: toggle
        debounce_ms: 20
      difficulty_right:
        pin_a: 25       # F7
        pin_b: 5        # F8
        type: toggle
        debounce_ms: 20
      channel:
        pin_2: 6        # CRT shader position
        pin_3: 13       # CRT shader position
        type: toggle
        debounce_ms: 20
    
    power_led:
      pin: 12
    
    shader:
      retroarch_host: "127.0.0.1"
      retroarch_port: 55355
    
    shutdown:
      command: "sudo shutdown -h now"
      delay_ms: 500  # debounce delay before triggering shutdown
    
    logging:
      level: INFO
    ```
  - Create `tests/test_config.py`:
    - Test loading valid config file
    - Test missing required keys raises clear error
    - Test duplicate pin numbers raises error
    - Test invalid BCM pin numbers (out of range, reserved) raises error
    - Test pin_assignments property returns correct dict
    - Test debounce_ms property returns correct dict
    - Test default values applied when optional keys missing

  **Must NOT do**:
  - ⛔ Do NOT add cartridge-related config keys
  - ⛔ Do NOT add database or persistent storage
  - ⛔ Do NOT hardcode pin numbers in the Config class

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Straightforward config module with YAML loading — well-defined inputs/outputs
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 3)
  - **Parallel Group**: Wave 1 (after Task 1)
  - **Blocks**: Tasks 4, 5, 6, 7, 8
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/config.py` — Config.from_file() pattern with YAML loading, env var injection, UID normalization, validation. Adapt the same classmethod pattern but with switch-specific validation.
  - `/Users/rkeppner/Code/rfid-vcr/config/tapes.example.yaml` — Example YAML config structure to follow (simple, flat, well-commented)

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_config.py -v` → all tests pass
  - [ ] `python -c "from retropie2600.config import Config; c = Config.from_file('config/switches.example.yaml'); print(c.pin_assignments)"` → prints pin mapping dict

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Config loads and returns correct pin assignments
    Tool: Bash
    Preconditions: Package installed, config/switches.example.yaml exists
    Steps:
      1. Run: python -c "from retropie2600.config import Config; c = Config.from_file('config/switches.example.yaml'); print(c.pin_assignments)"
      2. Assert: output contains 'power' key with value 26
      3. Assert: output contains 'game_select' key with value 22
      4. Assert: output contains 'tv_type_color' or similar key with value 4
    Expected Result: Dict printed with all switch names mapped to BCM pin numbers
    Evidence: .sisyphus/evidence/task-2-config-load.txt

  Scenario: Config rejects duplicate pin numbers
    Tool: Bash
    Preconditions: A modified config YAML with two switches using pin 22
    Steps:
      1. Create a temp YAML with game_select.pin: 22 and game_reset.pin: 22
      2. Run: python -c "from retropie2600.config import Config; Config.from_file('/tmp/bad_config.yaml')"
      3. Assert: raises ValueError or ConfigError mentioning "duplicate" and pin 22
    Expected Result: Clear error message about duplicate pin assignment
    Evidence: .sisyphus/evidence/task-2-config-duplicate-error.txt

  Scenario: All config tests pass
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_config.py -v
      2. Assert: all tests pass, 0 failures
    Expected Result: Full green test suite
    Evidence: .sisyphus/evidence/task-2-config-tests.txt
  ```

  **Commit**: YES
  - Message: `feat: add configuration module with YAML loading and validation`
  - Files: `retropie2600/config.py`, `config/switches.example.yaml`, `tests/test_config.py`
  - Pre-commit: `pytest tests/test_config.py -v`

- [ ] 3. Test Infrastructure — Shared Fixtures with Mocked Hardware

  **What to do**:
  - Create `tests/conftest.py` with shared pytest fixtures:
    - `mock_pigpio`: Mock of `pigpio.pi()` instance — supports `set_mode()`, `set_glitch_filter()`, `callback()`, `read()`, `set_pull_up_down()`, `connected` property. Returns configurable pin states from `read()`.
    - `mock_evdev_uinput`: Mock of `evdev.UInput` — captures `write()` and `syn()` calls. Records all injected key events for assertion.
    - `mock_socket`: Mock of `socket.socket` — captures `sendto()` calls for UDP assertion.
    - `mock_subprocess`: Mock of `subprocess.run` — captures shutdown commands.
    - `tmp_config`: Fixture that creates a temporary valid YAML config file and returns its path.
  - All fixtures should be usable independently (no cross-dependencies)
  - Mock objects should track call history for assertion (e.g., `mock_pigpio.callback.call_args_list`)

  **Must NOT do**:
  - ⛔ Do NOT require Pi hardware for any fixture
  - ⛔ Do NOT import actual pigpio, evdev, or other Pi-specific libraries in fixtures

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Creating test fixtures is straightforward Python — well-defined mock interfaces
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2)
  - **Parallel Group**: Wave 1 (after Task 1)
  - **Blocks**: Tasks 4, 5, 6, 7, 8
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/rfid_monitor.py:17-21` — Graceful degradation pattern: `try: from pirc522 import RFID; except ImportError: RFID = None`. Each module should follow this pattern for its hardware imports.
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/led_controller.py` — No-op fallback pattern when hardware unavailable

  **Acceptance Criteria**:
  - [ ] `pytest tests/conftest.py --co` → fixtures discoverable, no import errors
  - [ ] Fixtures work without pigpio, evdev, or other Pi libraries installed

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Fixtures load without Pi hardware libraries
    Tool: Bash
    Preconditions: Running on macOS (no pigpio, evdev installed natively)
    Steps:
      1. Run: python -c "import tests.conftest"
      2. Assert: no ImportError (fixtures don't import hardware libs at module level)
      3. Run: pytest --co tests/
      4. Assert: fixtures listed in collection output
    Expected Result: All fixtures discoverable and importable on macOS
    Evidence: .sisyphus/evidence/task-3-fixtures-macos.txt
  ```

  **Commit**: YES
  - Message: `feat: add test fixtures with mocked pigpio, evdev, and socket`
  - Files: `tests/conftest.py`
  - Pre-commit: `pytest --co`

- [ ] 4. GPIO Monitor — pigpio Edge Detection and Typed Switch Events

  **What to do**:
  - Create `retropie2600/gpio_monitor.py`:
    - `SwitchEvent` dataclass: `switch_name: str`, `position: str` (e.g., "color", "bw", "a", "b", "pressed", "released", "on", "off"), `timestamp: float`
    - `SwitchType` enum: `MOMENTARY`, `TOGGLE`
    - `GPIOMonitor` class:
      - `__init__(self, config: Config, callback: Callable[[SwitchEvent], None])` — takes config for pin assignments and a single callback for all switch events
      - `start()`: Connect to pigpiod via `pigpio.pi()`. For each configured switch pin: set mode INPUT, set pull-up, set glitch filter (from config debounce_ms × 1000 for microseconds), register `pigpio.callback()` for EITHER_EDGE. Graceful degradation: if `pigpio` not available or `pi.connected` is False, log warning and run in stub mode (no-op).
      - `stop()`: Cancel all callbacks, disconnect from pigpiod
      - `read_all_states()`: Read current state of ALL toggle switch pins, return dict of switch_name → current position. Used for startup sync.
      - Internal `_on_edge(gpio, level, tick)`: Translate raw GPIO edge into typed `SwitchEvent` and fire callback. For toggle switches: determine which position pin triggered → emit event with that position name. For momentary switches: FALLING_EDGE → "pressed", RISING_EDGE → "released".
    - Follow graceful degradation pattern from rfid-vcr: `try: import pigpio; except ImportError: pigpio = None`
  - Create `tests/test_gpio_monitor.py`:
    - Test monitor starts and registers callbacks for all configured pins
    - Test edge callback produces correct SwitchEvent for each switch type
    - Test toggle switch: pin_a going LOW → event(switch="difficulty_left", position="a")
    - Test momentary switch: pin going LOW → event(switch="game_select", position="pressed")
    - Test read_all_states returns correct dict based on mock pin values
    - Test graceful degradation: when pigpio unavailable, monitor starts in stub mode without error
    - Test stop() cancels all callbacks
    - Test glitch filter is set with correct microsecond values from config

  **Must NOT do**:
  - ⛔ Do NOT call any action functions from within GPIOMonitor — it only emits events
  - ⛔ Do NOT import or reference Stella, RetroArch, or shutdown logic
  - ⛔ Do NOT hardcode any pin numbers — all from config
  - ⛔ Do NOT use gpiozero or RPi.GPIO

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Core module with complex callback/event logic, hardware abstraction, and edge detection
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 5, 6, 7)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 2, 3

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/rfid_monitor.py:17-21` — Graceful degradation: `try: import X; except ImportError: X = None`
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/rfid_monitor.py:31-46` — Monitor class docstring pattern with Args section
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/rfid_monitor.py:98-159` — Poll loop pattern with state tracking and debounce (our approach is callback-based instead of polling, but the state tracking logic is similar)

  **External References**:
  - pigpio Python library: `pigpio.callback(pin, edge, func)` where func receives `(gpio, level, tick)`. `pi.set_glitch_filter(pin, microseconds)`. `pi.read(pin)` returns 0 or 1.
  - pigpio edge constants: `pigpio.EITHER_EDGE`, `pigpio.FALLING_EDGE`, `pigpio.RISING_EDGE`
  - pigpio pull-up: `pi.set_pull_up_down(pin, pigpio.PUD_UP)`

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_gpio_monitor.py -v` → all tests pass
  - [ ] `python -c "from retropie2600.gpio_monitor import GPIOMonitor, SwitchEvent, SwitchType"` → no import error

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: GPIO monitor emits correct events for toggle switch
    Tool: Bash
    Preconditions: mocked pigpio in tests
    Steps:
      1. Run: pytest tests/test_gpio_monitor.py -v -k "toggle"
      2. Assert: tests pass showing SwitchEvent with position="a" or position="b"
    Expected Result: Toggle switch produces typed events with correct position names
    Evidence: .sisyphus/evidence/task-4-gpio-toggle.txt

  Scenario: GPIO monitor emits correct events for momentary switch
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_gpio_monitor.py -v -k "momentary"
      2. Assert: tests pass showing SwitchEvent with position="pressed" on FALLING_EDGE
    Expected Result: Momentary switch produces "pressed" event on button push
    Evidence: .sisyphus/evidence/task-4-gpio-momentary.txt

  Scenario: Graceful degradation without pigpio
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_gpio_monitor.py -v -k "stub"
      2. Assert: test passes — monitor starts without error when pigpio unavailable
    Expected Result: No crash, warning logged, stub mode active
    Evidence: .sisyphus/evidence/task-4-gpio-stub.txt

  Scenario: Full GPIO monitor test suite
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_gpio_monitor.py -v
      2. Assert: all tests pass, 0 failures
    Expected Result: Complete green test suite
    Evidence: .sisyphus/evidence/task-4-gpio-full.txt
  ```

  **Commit**: YES
  - Message: `feat: add GPIO monitor with pigpio edge detection and switch events`
  - Files: `retropie2600/gpio_monitor.py`, `tests/test_gpio_monitor.py`
  - Pre-commit: `pytest tests/test_gpio_monitor.py -v`

- [ ] 5. Input Injector — Stella Keyboard Events via evdev/uinput

  **What to do**:
  - Create `retropie2600/input_injector.py`:
    - `STELLA_KEYS` dict mapping switch event identifiers to evdev key codes:
      - `"game_select"` → `ecodes.KEY_F1`
      - `"game_reset"` → `ecodes.KEY_F2`
      - `"tv_type_color"` → `ecodes.KEY_F3`
      - `"tv_type_bw"` → `ecodes.KEY_F4`
      - `"difficulty_left_a"` → `ecodes.KEY_F5`
      - `"difficulty_left_b"` → `ecodes.KEY_F6`
      - `"difficulty_right_a"` → `ecodes.KEY_F7`
      - `"difficulty_right_b"` → `ecodes.KEY_F8`
    - `InputInjector` class:
      - `__init__(self, device_name: str = "retropie2600-switches")` — creates a uinput virtual keyboard device with only the F1-F8 keys registered
      - `press_key(self, key_name: str)` — look up key code from STELLA_KEYS, send KEY_DOWN + SYN + brief delay + KEY_UP + SYN. This simulates a keypress.
      - `close()` — close the uinput device
      - Graceful degradation: if `evdev` not available, log warning and run in stub mode (press_key does nothing)
    - Follow the same `try: import evdev; except ImportError: evdev = None` pattern
  - Create `tests/test_input_injector.py`:
    - Test all 8 Stella key mappings are present and correct
    - Test press_key sends correct evdev key code sequence (KEY_DOWN, SYN, KEY_UP, SYN)
    - Test press_key with unknown key name logs warning and does nothing (no crash)
    - Test graceful degradation: stub mode when evdev unavailable
    - Test close() cleans up uinput device

  **Must NOT do**:
  - ⛔ Do NOT use xdotool or subprocess for key injection
  - ⛔ Do NOT register keys beyond F1-F8 (minimal attack surface)
  - ⛔ Do NOT handle shader or shutdown events — those go through different controllers

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires understanding of Linux evdev/uinput API and keycode constants
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 4, 6, 7)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 2, 3

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/led_controller.py` — Graceful degradation pattern with hardware fallback to no-op

  **External References**:
  - python-evdev UInput: `from evdev import UInput, ecodes`. `ui = UInput(name="name", events={ecodes.EV_KEY: [ecodes.KEY_F1, ...]})`
  - Key injection: `ui.write(ecodes.EV_KEY, ecodes.KEY_F1, 1)` (down), `ui.syn()`, `ui.write(ecodes.EV_KEY, ecodes.KEY_F1, 0)` (up), `ui.syn()`

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_input_injector.py -v` → all tests pass
  - [ ] `python -c "from retropie2600.input_injector import InputInjector, STELLA_KEYS"` → no import error

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: All Stella key mappings present
    Tool: Bash
    Steps:
      1. Run: python -c "from retropie2600.input_injector import STELLA_KEYS; print(list(STELLA_KEYS.keys()))"
      2. Assert: output contains all 8 keys: game_select, game_reset, tv_type_color, tv_type_bw, difficulty_left_a, difficulty_left_b, difficulty_right_a, difficulty_right_b
    Expected Result: All 8 Stella switch mappings present
    Evidence: .sisyphus/evidence/task-5-stella-keys.txt

  Scenario: Input injector test suite passes
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_input_injector.py -v
      2. Assert: all tests pass, 0 failures
    Expected Result: Complete green test suite
    Evidence: .sisyphus/evidence/task-5-injector-tests.txt
  ```

  **Commit**: YES
  - Message: `feat: add input injector for Stella keyboard events via evdev`
  - Files: `retropie2600/input_injector.py`, `tests/test_input_injector.py`
  - Pre-commit: `pytest tests/test_input_injector.py -v`

- [ ] 6. Shader Controller — RetroArch UDP Network Commands

  **What to do**:
  - Create `retropie2600/shader_controller.py`:
    - `ShaderController` class:
      - `__init__(self, host: str = "127.0.0.1", port: int = 55355)` — stores RetroArch network command target
      - `toggle_shader(self)` — sends `SHADER_TOGGLE` via UDP datagram to RetroArch. Uses `socket.socket(socket.AF_INET, socket.SOCK_DGRAM)` with `sendto()`. Fire-and-forget (UDP — no response expected). Log the action. Catch and log `OSError` (RetroArch not running = connection refused for UDP is unusual, but handle `socket.error` gracefully).
      - `send_command(self, command: str)` — generic RetroArch network command sender (for extensibility within Phase 1 only — e.g., could add `PAUSE_TOGGLE` later if needed)
    - No graceful degradation needed — socket is available everywhere. Just handle errors.
  - Create `tests/test_shader_controller.py`:
    - Test toggle_shader sends correct UDP packet to configured host:port
    - Test send_command sends arbitrary command string
    - Test socket error is caught and logged (not raised)
    - Test custom host/port from config

  **Must NOT do**:
  - ⛔ Do NOT use netcat subprocess — use socket.sendto() directly
  - ⛔ Do NOT add shader selection logic — just toggle (on/off)
  - ⛔ Do NOT add TCP fallback or response parsing

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple UDP socket wrapper — one method, one socket call
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 4, 5, 7)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 2, 3

  **References**:

  **External References**:
  - RetroArch network command interface: `echo -n "SHADER_TOGGLE" | nc -u 127.0.0.1 55355`. Requires `network_cmd_enable = "true"` and `network_cmd_port = "55355"` in retroarch.cfg.

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_shader_controller.py -v` → all tests pass
  - [ ] `python -c "from retropie2600.shader_controller import ShaderController"` → no import error

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Shader controller sends correct UDP packet
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_shader_controller.py -v -k "toggle"
      2. Assert: test passes, mock socket.sendto called with b"SHADER_TOGGLE" to ("127.0.0.1", 55355)
    Expected Result: Correct UDP packet sent to RetroArch
    Evidence: .sisyphus/evidence/task-6-shader-udp.txt

  Scenario: Shader controller handles connection errors gracefully
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_shader_controller.py -v -k "error"
      2. Assert: test passes — OSError caught and logged, no exception raised
    Expected Result: Graceful error handling
    Evidence: .sisyphus/evidence/task-6-shader-error.txt
  ```

  **Commit**: YES
  - Message: `feat: add shader controller for RetroArch UDP commands`
  - Files: `retropie2600/shader_controller.py`, `tests/test_shader_controller.py`
  - Pre-commit: `pytest tests/test_shader_controller.py -v`

- [ ] 7. Shutdown Controller — Safe Power-Off Sequence

  **What to do**:
  - Create `retropie2600/shutdown_controller.py`:
    - `ShutdownController` class:
      - `__init__(self, command: str = "sudo shutdown -h now", delay_ms: int = 500)` — configurable shutdown command and debounce delay
      - `_shutting_down: bool` flag — prevents multiple simultaneous shutdown attempts
      - `initiate_shutdown(self)` — if not already shutting down: set flag, log clearly ("Safe shutdown initiated — system will halt in ~5 seconds"), wait `delay_ms` (debounce — prevents accidental triggers), then call `subprocess.run(command.split(), check=False)`. If on macOS or non-Pi platform, log "Shutdown skipped (not on target platform)" instead of running the command.
      - `is_shutting_down` property — read-only access to the shutdown flag (used by daemon to suppress other switch events during shutdown)
    - Platform detection: check `sys.platform` or existence of `/usr/bin/shutdown` to determine if shutdown command should actually execute
  - Create `tests/test_shutdown_controller.py`:
    - Test initiate_shutdown calls subprocess.run with correct command
    - Test double-call protection: second call while shutting down is ignored
    - Test is_shutting_down property reflects state correctly
    - Test delay_ms is respected before subprocess call
    - Test macOS/non-Pi platform skips actual shutdown (uses mock subprocess)
    - Test custom shutdown command from config

  **Must NOT do**:
  - ⛔ Do NOT call os._exit() or sys.exit() — let systemd handle process lifecycle
  - ⛔ Do NOT combine shutdown logic with GPIO monitoring
  - ⛔ Do NOT add reboot functionality — only shutdown

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple subprocess wrapper with a flag and platform check
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 4, 5, 6)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 2, 3

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/main.py:186-189` — Signal handling pattern: set event flag, don't call exit directly

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_shutdown_controller.py -v` → all tests pass
  - [ ] `python -c "from retropie2600.shutdown_controller import ShutdownController"` → no import error

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Shutdown controller calls correct command
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_shutdown_controller.py -v -k "initiate"
      2. Assert: test passes, mock subprocess.run called with ["sudo", "shutdown", "-h", "now"]
    Expected Result: Correct shutdown command issued
    Evidence: .sisyphus/evidence/task-7-shutdown-command.txt

  Scenario: Double-shutdown protection works
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_shutdown_controller.py -v -k "double"
      2. Assert: test passes — subprocess.run called exactly once despite two initiate_shutdown() calls
    Expected Result: Second shutdown attempt silently ignored
    Evidence: .sisyphus/evidence/task-7-shutdown-double.txt
  ```

  **Commit**: YES
  - Message: `feat: add shutdown controller for safe power-off sequence`
  - Files: `retropie2600/shutdown_controller.py`, `tests/test_shutdown_controller.py`
  - Pre-commit: `pytest tests/test_shutdown_controller.py -v`

- [ ] 8. Main Daemon — Systemd Integration, Event Routing, and Startup Sync

  **What to do**:
  - Create `retropie2600/daemon.py`:
    - `RetroPie2600Daemon` class following the exact pattern from `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/main.py:32-111`:
      - `__init__(self, config_path: str)` — stores config path, initializes None references for subsystems
      - `run(self) -> int` — main entry point:
        1. Load Config from YAML
        2. Initialize GPIOMonitor with `self._on_switch_event` callback
        3. Initialize InputInjector
        4. Initialize ShaderController with config host/port
        5. Initialize ShutdownController with config command/delay
        6. Register signal handlers (SIGTERM, SIGINT) → set shutdown event
        7. Start GPIOMonitor
        8. **Startup sync**: Call `gpio_monitor.read_all_states()`, for each toggle switch in a non-default position, fire the corresponding key injection to sync Stella's state. Log each sync action.
        9. sdnotify READY=1 (via `sdnotify` library — import with try/except, provide no-op stub if unavailable on macOS; `sdnotify` is a Linux-only dep declared with PEP 508 marker in pyproject.toml)
        10. Main loop: `while not shutdown_event.wait(timeout=WATCHDOG_INTERVAL): notify WATCHDOG=1` (watchdog also uses sdnotify with same graceful fallback)
        11. Ordered shutdown: stop monitor → close injector → log done
        12. Return 0 on clean exit, 1 on fatal error
      - `_on_switch_event(self, event: SwitchEvent)` — event router:
        - If `shutdown_controller.is_shutting_down`: log and ignore (race condition protection)
        - If event.switch_name == "power" and event.position == "off": call `shutdown_controller.initiate_shutdown()`
        - If event.switch_name == "channel": call `shader_controller.toggle_shader()`
        - If event.switch_name in Stella switches: construct key_name from switch_name + position (e.g., "difficulty_left" + "a" → "difficulty_left_a"), call `input_injector.press_key(key_name)`
        - For momentary switches (select, reset): only fire on "pressed", ignore "released"
    - CLI entry point (same pattern as rfid-vcr `main.py:213-248`):
      - `argparse` with `--config` (default: `config/switches.yaml`) and `--log-level`
      - `main(argv=None) -> int` function
      - `if __name__ == "__main__": sys.exit(main())`
    - Support `python -m retropie2600.daemon` via `__main__.py` in the package
  - Create `retropie2600/__main__.py`:
    - `from retropie2600.daemon import main; import sys; sys.exit(main())`
  - Create `tests/test_daemon.py`:
    - Test daemon loads config and initializes all subsystems
    - Test event routing: power off event → shutdown controller called
    - Test event routing: channel event → shader controller called
    - Test event routing: game_select pressed → input injector called with "game_select"
    - Test event routing: game_select released → input injector NOT called (momentary: only fire on press)
    - Test event routing: tv_type color → input injector called with "tv_type_color"
    - Test event routing: events ignored when is_shutting_down is True
    - Test startup sync: reads toggle states and fires initial key events
    - Test sdnotify fallback: when sdnotify import fails (macOS), daemon still starts without error — verify no-op notifier is used
    - Test signal handling: SIGTERM sets shutdown event
    - Test CLI: `--help` shows usage, `--config` and `--log-level` accepted
    - Test graceful shutdown sequence order: stop monitor before closing injector

  **Must NOT do**:
  - ⛔ Do NOT add any Phase 2 logic (cartridge detection, ROM reading)
  - ⛔ Do NOT add REST API, web interface, or health endpoints
  - ⛔ Do NOT add automatic restart logic — let systemd handle that

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Integration module wiring all subsystems together — requires understanding all component interfaces, event routing, lifecycle management, and startup sync logic
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (sequential — depends on all Wave 2 tasks)
  - **Blocks**: Tasks 9, 12
  - **Blocked By**: Tasks 4, 5, 6, 7

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/main.py:32-111` — **PRIMARY REFERENCE**: RFIDVCRDaemon class. Follow this exact structure: __init__ with None refs → run() with ordered init → signal handlers → main loop → ordered shutdown. The startup sync (`_check_startup_tag` at line 98-99) maps to our toggle state sync.
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/main.py:117-143` — `_on_tag_arrived` callback pattern: lookup config → LED control → action. Our `_on_switch_event` follows the same lookup → route → act pattern.
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/main.py:186-206` — Signal handling and ordered shutdown. Follow this exactly: set event → stop subsystems in reverse init order.
  - `/Users/rkeppner/Code/rfid-vcr/rfid_vcr/main.py:213-248` — CLI entry point with argparse. Copy this pattern for --config and --log-level.

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_daemon.py -v` → all tests pass
  - [ ] `pytest tests/ -v` → full suite passes (all modules integrated)
  - [ ] `python -m retropie2600.daemon --help` → prints usage with --config and --log-level
  - [ ] `python -c "from retropie2600.daemon import RetroPie2600Daemon, main"` → no import error

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Daemon CLI shows help
    Tool: Bash
    Steps:
      1. Run: python -m retropie2600.daemon --help
      2. Assert: output contains "--config" and "--log-level" and "retropie2600"
    Expected Result: Help text with both options displayed
    Evidence: .sisyphus/evidence/task-8-daemon-help.txt

  Scenario: Event routing works for all switch types
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_daemon.py -v -k "routing"
      2. Assert: all routing tests pass — power→shutdown, channel→shader, select→injector, tv_type→injector
    Expected Result: Every switch type routed to correct controller
    Evidence: .sisyphus/evidence/task-8-daemon-routing.txt

  Scenario: Startup sync reads and applies toggle states
    Tool: Bash
    Steps:
      1. Run: pytest tests/test_daemon.py -v -k "startup_sync"
      2. Assert: test passes — mock input_injector.press_key called for each toggle in non-default position
    Expected Result: Toggle states synced at daemon start
    Evidence: .sisyphus/evidence/task-8-daemon-startup-sync.txt

  Scenario: Full test suite passes
    Tool: Bash
    Steps:
      1. Run: pytest tests/ -v
      2. Assert: all tests across ALL test files pass, 0 failures
    Expected Result: Complete green test suite for entire project
    Evidence: .sisyphus/evidence/task-8-full-suite.txt
  ```

  **Commit**: YES
  - Message: `feat: add main daemon with systemd integration and startup sync`
  - Files: `retropie2600/daemon.py`, `retropie2600/__main__.py`, `tests/test_daemon.py`
  - Pre-commit: `pytest tests/ -v`

- [ ] 9. Systemd Service Unit and udev Rules

  **What to do**:
  - Create `systemd/retropie2600.service` following the pattern from `/Users/rkeppner/Code/rfid-vcr/systemd/rfid-vcr.service`:
    - `[Unit]` section: Description, After=pigpiod.service + multi-user.target, Requires=pigpiod.service
    - `[Service]` section: Type=notify, User=pi, Group=pi, SupplementaryGroups=gpio input (need both for pigpio and uinput), WorkingDirectory=/opt/retropie2600, ExecStart=/opt/retropie2600/venv/bin/python -m retropie2600.daemon --config /etc/retropie2600/switches.yaml, WatchdogSec=30, Restart=on-failure, RestartSec=5, EnvironmentFile=-/etc/retropie2600/env
    - `[Install]` section: WantedBy=multi-user.target
  - Create `systemd/99-retropie2600.rules` — udev rules for GPIO and uinput access:
    - `SUBSYSTEM=="input", ATTRS{name}=="retropie2600-switches", ENV{ID_INPUT_KEYBOARD}="1"` — ensures EmulationStation/RetroArch sees our virtual keyboard
    - Any necessary uinput permissions for the service user
  - Create `config/env.example` — example environment file (may be empty for Phase 1, but establishes the pattern)

  **Must NOT do**:
  - ⛔ Do NOT hardcode paths — use standard /opt/ and /etc/ locations
  - ⛔ Do NOT add Docker or container orchestration

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Templating systemd unit file from existing reference
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 10)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 12
  - **Blocked By**: Task 8

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/systemd/rfid-vcr.service` — **PRIMARY REFERENCE**: systemd unit file with Type=notify, WatchdogSec, User/Group, SupplementaryGroups, EnvironmentFile. Adapt this structure with different ExecStart, After dependencies, and SupplementaryGroups.
  - `/Users/rkeppner/Code/rfid-vcr/systemd/99-spi.rules` — udev rules pattern. Adapt for uinput instead of SPI.

  **Acceptance Criteria**:
  - [ ] `systemd-analyze verify systemd/retropie2600.service` → no errors (on Linux)
  - [ ] Service file references correct ExecStart path and config path

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: systemd service file is syntactically valid
    Tool: Bash
    Preconditions: Linux system (skip on macOS with clear message)
    Steps:
      1. Run: systemd-analyze verify systemd/retropie2600.service 2>&1 || echo "SKIP: not on Linux"
      2. If on Linux: assert no error output
      3. If on macOS: Run: grep -q "Type=notify" systemd/retropie2600.service && grep -q "After=pigpiod.service" systemd/retropie2600.service
      4. Assert: both grep commands succeed (exit code 0)
    Expected Result: Service file contains required directives
    Evidence: .sisyphus/evidence/task-9-systemd-verify.txt

  Scenario: udev rules file exists with correct content
    Tool: Bash
    Steps:
      1. Run: grep "retropie2600-switches" systemd/99-retropie2600.rules
      2. Assert: output contains the virtual keyboard rule
    Expected Result: udev rule for virtual keyboard device present
    Evidence: .sisyphus/evidence/task-9-udev-rules.txt
  ```

  **Commit**: YES
  - Message: `feat: add systemd service unit and deployment config`
  - Files: `systemd/retropie2600.service`, `systemd/99-retropie2600.rules`, `config/env.example`
  - Pre-commit: —

- [ ] 10. RetroArch and lr-stella Configuration Files

  **What to do**:
  - Create `config/retroarch.cfg.example` with the specific settings needed:
    - `network_cmd_enable = "true"` — enables UDP network commands (required for shader toggle)
    - `network_cmd_port = "55355"` — default port for network commands
    - `video_shader_enable = "true"` — enables CRT shaders
    - `video_shader = "/opt/retropie/emulators/retroarch/shader/shaders_glsl/crt/zfast-crt.glslp"` — recommended CRT shader for Pi 3B+ GPU
    - `input_shader_toggle` key binding (as fallback to UDP)
    - Any lr-stella-specific core options that map console switches correctly
  - Create `docs/retroarch-setup.md`:
    - Brief guide explaining how to configure RetroArch for the daemon
    - Which settings are required (network commands) vs optional (shader)
    - How to install the zfast-crt shader if not present
    - How to verify the shader toggle works manually (test with `echo -n "SHADER_TOGGLE" | nc -u 127.0.0.1 55355`)
    - lr-stella core options reference

  **Must NOT do**:
  - ⛔ Do NOT modify actual RetroArch config files — only provide examples
  - ⛔ Do NOT automate RetroArch installation — that's part of RetroPie
  - ⛔ Do NOT add shader selection UI — just toggle on/off

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Creating config example files with documentation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Tasks 8, 9)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 12
  - **Blocked By**: Task 1

  **References**:

  **External References**:
  - RetroArch network command interface: requires `network_cmd_enable = "true"` in retroarch.cfg
  - zfast-crt shader: recommended for Pi 3B+ GPU performance. Path varies by RetroPie installation.
  - lr-stella core options: accessible via RetroArch Quick Menu → Options

  **Acceptance Criteria**:
  - [ ] `config/retroarch.cfg.example` exists and contains `network_cmd_enable`
  - [ ] `docs/retroarch-setup.md` exists and covers network command setup

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: RetroArch config example contains required settings
    Tool: Bash
    Steps:
      1. Run: grep "network_cmd_enable" config/retroarch.cfg.example
      2. Assert: output contains 'network_cmd_enable = "true"'
      3. Run: grep "network_cmd_port" config/retroarch.cfg.example
      4. Assert: output contains '55355'
      5. Run: grep "video_shader_enable" config/retroarch.cfg.example
      6. Assert: output contains 'video_shader_enable = "true"'
    Expected Result: All required RetroArch settings present
    Evidence: .sisyphus/evidence/task-10-retroarch-config.txt

  Scenario: RetroArch setup docs exist with required sections
    Tool: Bash
    Steps:
      1. Run: grep -c "network" docs/retroarch-setup.md
      2. Assert: at least 2 matches (mentions network commands)
      3. Run: grep -c "shader" docs/retroarch-setup.md
      4. Assert: at least 2 matches (mentions shader setup)
    Expected Result: Documentation covers both network commands and shaders
    Evidence: .sisyphus/evidence/task-10-retroarch-docs.txt
  ```

  **Commit**: YES
  - Message: `feat: add RetroArch and lr-stella configuration examples`
  - Files: `config/retroarch.cfg.example`, `docs/retroarch-setup.md`
  - Pre-commit: —

- [ ] 11. Hardware Wiring Guide — GPIO Pinout, Switch Connections, Power, Cooling

  **What to do**:
  - Create `docs/hardware-guide.md` — comprehensive hardware assembly guide:
    - **Bill of Materials (BOM)**:
      - Raspberry Pi 3B+ with microSD card
      - 2× 2600-daptor 2e USB adapters
      - 2× USB panel-mount extension cables
      - 1× Ethernet panel-mount extension cable
      - 1× 5V micro-USB power supply (2.5A+)
      - 1× 40mm 5V fan with heatsink kit
      - 1× Red LED (3mm or 5mm) + 330Ω resistor
      - DuPont female-to-female jumper wires (at least 12)
      - Solder + soldering iron for board pad connections
      - Dremel or rotary tool for port cutouts
    - **GPIO Pin Assignment Table** (matching config/switches.example.yaml defaults):
      | Switch | BCM Pin(s) | Physical Pin(s) | Notes |
      |--------|-----------|----------------|-------|
      | Power (shutdown) | 26 | 37 | Software shutdown trigger |
      | TV Type Color | 4 | 7 | F3 |
      | TV Type B&W | 17 | 11 | F4 |
      | Game Select | 22 | 15 | F1 (momentary) |
      | Game Reset | 27 | 13 | F2 (momentary) |
      | Left Difficulty A | 23 | 16 | F5 |
      | Left Difficulty B | 24 | 18 | F6 |
      | Right Difficulty A | 25 | 22 | F7 |
      | Right Difficulty B | 5 | 29 | F8 |
      | Channel 2 | 6 | 31 | CRT shader |
      | Channel 3 | 13 | 33 | CRT shader |
      | Power LED | 12 | 32 | Red LED |
      | Fan | via 5V + GND | 4+6 | Direct to 5V rail |
    - **Switch Wiring Instructions**:
      - How to identify the 4-pin common and 2-pin signal groups on DPDT switches using a multimeter
      - Wiring diagram (ASCII art) for each switch type (toggle vs momentary)
      - Pull-up resistor explanation (using Pi's internal pull-ups via pigpio)
      - Solder points on the Atari board where IC pads provide access to switch traces
      - DuPont connector attachment on the Pi GPIO header end
    - **Power LED Installation**:
      - Red LED + 330Ω resistor wired to GPIO 12 (3.3V output) and GND
      - Mounting in the original power jack hole
    - **Fan Installation**:
      - 40mm 5V fan wired directly to Pi 5V and GND pins
      - Mounting position: near top vents for exhaust
      - Optional: `dtoverlay=gpio-fan` for temperature-controlled activation
    - **Port Cutout Guide**:
      - Where to Dremel for HDMI, micro-USB power, 3.5mm audio, USB extenders, ethernet
      - Pi orientation against back of case
    - **Safety Warnings** (CRITICAL):
      - ⚠️ 5V logic on Atari board traces can destroy 3.3V Pi GPIO — verify with multimeter that no switch pad has voltage before connecting
      - ⚠️ ESD precautions when handling Pi and wiring
      - ⚠️ Proper grounding: common ground bus between Pi GND and Atari board ground
      - ⚠️ Wire routing: keep away from fan, avoid shorts, use cable ties
    - **dtoverlay configuration** for /boot/config.txt:
      - `dtoverlay=gpio-shutdown,gpio_pin=26` — enables wake-from-halt via power switch
      - `dtoverlay=gpio-fan,gpiopin=X,temp=60000` — optional fan temperature control

  **Must NOT do**:
  - ⛔ Do NOT include Phase 2 cartridge wiring (level shifters, GPIO expanders)
  - ⛔ Do NOT include buck converter wiring (using standard Pi PSU)

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Technical documentation with diagrams, tables, and step-by-step instructions
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 12)
  - **Parallel Group**: Wave 4
  - **Blocks**: None
  - **Blocked By**: None (can reference config defaults without code being complete)

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/docs/hardware-guide.md` — **PRIMARY REFERENCE**: Hardware guide format from RFID-VCR project. Follow same structure: BOM, wiring, safety, testing.

  **Acceptance Criteria**:
  - [ ] `docs/hardware-guide.md` exists
  - [ ] Contains BOM section with all components listed
  - [ ] Contains GPIO pin assignment table with BCM and physical pin numbers
  - [ ] Contains safety warnings section
  - [ ] All BCM pin numbers match defaults in `config/switches.example.yaml`

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Hardware guide contains all required sections
    Tool: Bash
    Steps:
      1. Run: grep -c "BOM\|Bill of Materials" docs/hardware-guide.md
      2. Assert: at least 1 match
      3. Run: grep -c "GPIO\|Pin Assignment" docs/hardware-guide.md
      4. Assert: at least 2 matches
      5. Run: grep -c "Safety\|Warning\|⚠️\|CRITICAL" docs/hardware-guide.md
      6. Assert: at least 2 matches
      7. Run: grep "BCM 26\|gpio_pin=26\|pin: 26" docs/hardware-guide.md
      8. Assert: power switch pin reference present
    Expected Result: All required sections and pin references present
    Evidence: .sisyphus/evidence/task-11-hardware-guide.txt

  Scenario: Pin numbers in docs match config defaults
    Tool: Bash
    Steps:
      1. Run: python3 -c "import yaml; pins = [str(v) for d in yaml.safe_load(open('config/switches.example.yaml'))['switches'].values() for k,v in (d.items() if isinstance(d,dict) else []) if 'pin' in str(k)]; print('\n'.join(sorted(set(pins))))"
      2. Run: python3 -c "import re; text = open('docs/hardware-guide.md').read(); pins = re.findall(r'BCM\s*(\d+)', text); print('\n'.join(sorted(set(pins))))"
      3. Compare: all config pin numbers appear in hardware guide (both commands produce sorted unique pin lists)
    Expected Result: Pin numbers are consistent between config and docs
    Failure Indicators: Pin number present in config but missing from hardware guide, or vice versa
    Evidence: .sisyphus/evidence/task-11-pin-consistency.txt
  ```

  **Commit**: YES
  - Message: `docs: add hardware wiring guide with GPIO pinout and circuit diagram`
  - Files: `docs/hardware-guide.md`
  - Pre-commit: —

- [ ] 12. Installation Guide — Complete RetroPie Setup and Daemon Deployment

  **What to do**:
  - Create `docs/installation.md` — step-by-step installation guide:
    - **RetroPie Base Setup**:
      - Flash RetroPie image (latest) to microSD
      - Initial boot, SSH access, WiFi configuration
      - Update RetroPie: `sudo apt update && sudo apt upgrade`
      - Install lr-stella if not present: via RetroPie-Setup menu
    - **System Dependencies**:
      - Enable pigpiod: `sudo systemctl enable pigpiod && sudo systemctl start pigpiod`
      - Install python3-venv if needed: `sudo apt install python3-venv`
    - **Daemon Installation**:
      - Clone repo or copy to `/opt/retropie2600/`
      - Create venv: `python3 -m venv /opt/retropie2600/venv`
      - Install: `/opt/retropie2600/venv/bin/pip install -e /opt/retropie2600/`
      - Create config directory: `sudo mkdir -p /etc/retropie2600/`
      - Copy and customize config: `sudo cp config/switches.example.yaml /etc/retropie2600/switches.yaml`
      - Edit pin assignments if wiring differs from defaults
    - **systemd Service Setup**:
      - Copy service file: `sudo cp systemd/retropie2600.service /etc/systemd/system/`
      - Copy udev rules: `sudo cp systemd/99-retropie2600.rules /etc/udev/rules.d/`
      - Reload: `sudo systemctl daemon-reload && sudo udevadm control --reload-rules`
      - Enable and start: `sudo systemctl enable retropie2600 && sudo systemctl start retropie2600`
      - Verify: `sudo systemctl status retropie2600`
    - **RetroArch Configuration**:
      - Reference `docs/retroarch-setup.md` for network command and shader setup
      - How to apply config changes
    - **Boot Configuration** (/boot/config.txt):
      - `dtoverlay=gpio-shutdown,gpio_pin=26` — for power switch wake-from-halt
      - `dtoverlay=gpio-fan,gpiopin=X,temp=60000` — optional fan control
    - **2600-daptor 2e Setup**:
      - Plug in both adapters
      - Configure in RetroPie: Input Configuration
      - Note: 2600-daptor 2e is natively supported by RetroPie/Linux as a USB HID device
    - **Verification Steps**:
      - Test each switch individually via `journalctl -u retropie2600 -f`
      - Test shader toggle: start a game, flip channel switch, observe CRT shader toggle
      - Test power switch: flip to OFF, observe safe shutdown
      - Test power switch: flip to ON, observe boot from halt

  **Must NOT do**:
  - ⛔ Do NOT include Phase 2 cartridge setup
  - ⛔ Do NOT automate installation with a script (keep it manual and explicit)
  - ⛔ Do NOT include Docker deployment

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Technical documentation with step-by-step commands
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 11)
  - **Parallel Group**: Wave 4
  - **Blocks**: None
  - **Blocked By**: Tasks 9, 10

  **References**:

  **Pattern References**:
  - `/Users/rkeppner/Code/rfid-vcr/docs/pi-setup.md` — **PRIMARY REFERENCE**: Pi setup guide from RFID-VCR. Follow same format: system prep → dependencies → daemon install → service setup → verification.

  **Acceptance Criteria**:
  - [ ] `docs/installation.md` exists
  - [ ] Contains RetroPie setup section
  - [ ] Contains daemon installation commands
  - [ ] Contains systemd service setup commands
  - [ ] Contains verification steps

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Installation guide contains all required sections
    Tool: Bash
    Steps:
      1. Run: grep -c "RetroPie\|retropie" docs/installation.md
      2. Assert: at least 3 matches
      3. Run: grep -c "systemctl" docs/installation.md
      4. Assert: at least 3 matches (enable, start, status)
      5. Run: grep -c "pigpiod" docs/installation.md
      6. Assert: at least 1 match
      7. Run: grep -c "2600-daptor\|daptor" docs/installation.md
      8. Assert: at least 1 match
      9. Run: grep -c "gpio-shutdown" docs/installation.md
      10. Assert: at least 1 match
    Expected Result: All major topics covered
    Evidence: .sisyphus/evidence/task-12-installation-guide.txt

  Scenario: Installation commands are syntactically plausible
    Tool: Bash
    Steps:
      1. Run: grep "sudo\|pip install\|systemctl\|mkdir" docs/installation.md | head -10
      2. Assert: commands look like valid shell commands (not pseudocode)
    Expected Result: Real, executable commands in the guide
    Evidence: .sisyphus/evidence/task-12-install-commands.txt
  ```

  **Commit**: YES
  - Message: `docs: add complete installation guide for RetroPie setup`
  - Files: `docs/installation.md`
  - Pre-commit: —

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run linter + `pytest tests/ -v`. Review all Python files for: `as Any`, bare `except:`, `# type: ignore` without justification, empty except blocks, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic variable names. Verify all modules have proper docstrings.
  Output: `Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real QA** — `unspecified-high`
  Start from clean state. Run `pytest tests/ -v` and capture full output. Verify all imports work: `python -c "from retropie2600 import ..."`. Load example config: `python -c "from retropie2600.config import Config; ..."`. Run daemon help: `python -m retropie2600.daemon --help`. Verify all docs exist and contain required sections.
  Output: `Tests [N/N pass] | Imports [PASS/FAIL] | Config [PASS/FAIL] | Daemon CLI [PASS/FAIL] | Docs [N/N present] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual code. Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT Have" compliance — search for CartridgeMonitor, CartridgeReader, ROMHasher, gpiozero, RPi.GPIO, xdotool, abstract base classes. Flag any Phase 2 code.
  Output: `Tasks [N/N compliant] | Scope [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

| Commit | Message | Key Files | Pre-commit Check |
|--------|---------|-----------|-----------------|
| 1 | `feat: add project scaffolding with package structure and dev deps` | pyproject.toml, retropie2600/__init__.py, tests/, .gitignore | `pytest` runs (0 tests, no errors) |
| 2 | `feat: add configuration module with YAML loading and validation` | retropie2600/config.py, config/switches.example.yaml, tests/test_config.py | `pytest tests/test_config.py -v` |
| 3 | `feat: add test fixtures with mocked pigpio, evdev, and socket` | tests/conftest.py | `pytest` runs |
| 4 | `feat: add GPIO monitor with pigpio edge detection and switch events` | retropie2600/gpio_monitor.py, tests/test_gpio_monitor.py | `pytest tests/test_gpio_monitor.py -v` |
| 5 | `feat: add input injector for Stella keyboard events via evdev` | retropie2600/input_injector.py, tests/test_input_injector.py | `pytest tests/test_input_injector.py -v` |
| 6 | `feat: add shader controller for RetroArch UDP commands` | retropie2600/shader_controller.py, tests/test_shader_controller.py | `pytest tests/test_shader_controller.py -v` |
| 7 | `feat: add shutdown controller for safe power-off sequence` | retropie2600/shutdown_controller.py, tests/test_shutdown_controller.py | `pytest tests/test_shutdown_controller.py -v` |
| 8 | `feat: add main daemon with systemd integration and startup sync` | retropie2600/daemon.py, tests/test_daemon.py | `pytest tests/ -v` (full suite) |
| 9 | `feat: add systemd service unit and deployment config` | systemd/retropie2600.service, systemd/99-gpio.rules | — |
| 10 | `feat: add RetroArch and lr-stella configuration examples` | config/retroarch.cfg.example, docs/retroarch-setup.md | — |
| 11 | `docs: add hardware wiring guide with GPIO pinout and circuit diagram` | docs/hardware-guide.md | — |
| 12 | `docs: add complete installation guide for RetroPie setup` | docs/installation.md | — |

---

## Success Criteria

### Verification Commands
```bash
# All tests pass on macOS
pytest tests/ -v  # Expected: all pass, 0 failures

# Daemon CLI works
python -m retropie2600.daemon --help  # Expected: usage with --config and --log-level

# All modules importable
python -c "from retropie2600 import config, gpio_monitor, input_injector, shader_controller, shutdown_controller, daemon"  # Expected: no errors

# Config loads
python -c "from retropie2600.config import Config; c = Config.from_file('config/switches.example.yaml'); print(c.pin_assignments)"  # Expected: prints dict of pin assignments

# Docs exist
ls docs/hardware-guide.md docs/installation.md  # Expected: both files exist
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass on macOS
- [ ] Config example is valid and loads without errors
- [ ] Hardware guide covers all switches, power LED, fan, and safety warnings
- [ ] Installation guide covers RetroPie setup, daemon installation, and service enablement
- [ ] All GPIO pin references consistent between docs, config, and code defaults

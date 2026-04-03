# Hardware Guide Upgrade — IC Socket Wiring Diagrams & Documentation

## TL;DR

> **Quick Summary**: Rewrite `docs/hardware-guide.md` to include detailed IC socket pin-to-GPIO wiring instructions with hand-coded SVG diagrams, enabling a builder to wire original Atari 2600 CX-2600A switches to a Raspberry Pi 3B+ using the empty chip socket holes as solder points.
> 
> **Deliverables**:
> - 3 SVG diagrams in `docs/diagrams/` (RIOT socket pinout, Pi GPIO header, full wiring diagram)
> - Rewritten `docs/hardware-guide.md` (~300+ lines) with IC socket mapping, embedded diagrams, step-by-step wiring, and 5V overvoltage mitigation
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 2 waves
> **Critical Path**: Task 1 (SVGs) → Task 2 (Markdown rewrite)

---

## Context

### Original Request
The user needs much better documentation for wiring Atari 2600 CX-2600A switches to Raspberry Pi GPIO. The original IC chips (6507, TIA, 6532 RIOT) have been removed, leaving empty IC sockets. The user wants to leverage these empty socket pin holes as preferred solder points. Visual image diagrams are required — not just ASCII art.

### Interview Summary
**Key Discussions**:
- All 5 console switches (RESET, SELECT, B/W-COLOR, DIFF LEFT, DIFF RIGHT) route through the 6532 RIOT (A202) IC socket only — TIA socket is not needed for console switches
- DJSures' Arduino project confirms the IC-socket-pad approach works in practice
- Board has 24K pull-up resistors to +5V on switch lines — 5V overvoltage risk for Pi's 3.3V GPIO
- Recommended mitigation: remove the 24K pull-up resistors from the board and use Pi's internal pull-ups at 3.3V
- POWER and CHANNEL switches don't connect to IC sockets (voltage regulator and RF modulator respectively)

**Research Findings**:
- **Atari Field Service Manual (FD100133)**: Authoritative IC socket pin mappings — RIOT A202: Pin 24=RESET, Pin 23=SELECT, Pin 21=B/W-COLOR, Pin 17=DIFF LEFT, Pin 16=DIFF RIGHT, Pin 1=GND
- **DJSures/Atari-2600-VCS-USB-Joystick-Console-Arduino**: Confirms IC socket pad wiring approach works; 5 switches via INPUT_PULLUP
- **etheling/rpie2600**: Another Pi mod project confirming switch signal routing
- **Chester's Breadboard Atari**: Independently confirms RIOT Pin 24/PB0 = GAME RESET
- **GPIO monitor code**: Expects active-low logic (PUD_UP + level==0 = active), EITHER_EDGE callbacks
- **Inline SVG does NOT render on GitHub** — must use separate `.svg` files referenced via `![alt](path)`

### Metis Review
**Identified Gaps** (addressed):
- SVG rendering limitations on GitHub — must use external file references, not inline SVG
- Pin number triple-validation requirement — every pin must be verified against config YAML, gpio_monitor.py, AND Atari FSM
- 5V overvoltage warning must precede wiring instructions (not be buried in safety section)
- Directory naming: `docs/diagrams/` preferred over `docs/images/` for semantic accuracy
- SVG accessibility attributes (role="img", title, desc) required
- DPDT switch explanation needed (brief — why only one pole is used via IC socket pads)
- Ground connection options: RIOT Pin 1 as primary, but mention other board ground points
- Power switch distinction: handled by `gpio-shutdown` dtoverlay, not GPIO monitor

---

## Work Objectives

### Core Objective
Create comprehensive, visually-rich hardware wiring documentation that tells a builder exactly where on the Atari 2600 CX-2600A PCB to solder (empty IC socket pin holes), what each solder point connects to, and how to wire from those points to Raspberry Pi GPIO pins.

### Concrete Deliverables
- `docs/diagrams/6532-riot-socket.svg` — 40-pin DIP socket pinout diagram with switch pins highlighted
- `docs/diagrams/rpi-gpio-header.svg` — Pi 40-pin GPIO header with project pin assignments labeled
  - `docs/diagrams/atari-to-pi-wiring.svg` — Full wiring connection diagram between RIOT socket and Pi
  - `docs/hardware-guide.md` — Rewritten guide incorporating all above + IC socket mapping + step-by-step wiring
  - `config/switches.example.yaml` — Updated to single-pin toggle config matching IC socket wiring
  - `retropie2600/gpio_monitor.py` — Updated to support single-pin toggle detection (report both HIGH and LOW positions on a single pin)
  - Updated tests for new single-pin toggle behavior

### Definition of Done
- [ ] All 3 SVG files render correctly when viewed on GitHub
- [ ] `docs/hardware-guide.md` contains IC socket pin mapping table with triple-validated pin numbers
- [ ] 5V overvoltage warning appears before any wiring instructions
- [ ] Every BCM pin in `config/switches.example.yaml` appears in the hardware guide
- [ ] `config/switches.example.yaml` updated to single-pin toggle config
- [ ] `gpio_monitor.py` supports single-pin toggle detection (fires events for both HIGH and LOW)
- [ ] All tests pass (`bun test` / `pytest`)
- [ ] No unexpected files modified

### Must Have
- IC socket pin mapping table (RIOT socket pin → switch signal → Pi BCM pin)
- Hand-coded SVG diagrams (not screenshots or raster images)
- Step-by-step wiring instructions for each switch
- 5V overvoltage warning with pull-up resistor removal instructions
- SVG accessibility attributes (role="img", title, desc)
- Preservation of existing good content (BOM, safety warnings, /boot/config.txt, testing)
- Single-pin toggle support in `gpio_monitor.py` (fires events for both HIGH→position_a and LOW→position_b on one pin)
- Updated `config/switches.example.yaml` with single-pin toggle config matching IC socket wiring
- Updated tests verifying single-pin toggle behavior

### Must NOT Have (Guardrails)
- No inline SVG in markdown (GitHub strips it)
- No Mermaid diagrams as substitutes for pin/wiring SVGs
- No animated SVGs or dark-mode variants
- No photos/raster images (SVGs only for new diagrams)
- No changes to pin assignments that don't match the IC socket wiring approach
- No changes to README, installation.md, or retroarch-setup.md
- No embedded raster data or external dependencies in SVGs
- No `<script>` or `<foreignObject>` elements in SVGs
- Each SVG must be under 20KB
- No breaking changes to momentary switch behavior (RESET, SELECT must continue working as-is)
- No changes to daemon.py event routing logic — only gpio_monitor.py single-pin detection

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (62 pytest tests)
- **Automated tests**: YES (tests-after) — Task 5 adds tests for single-pin toggle behavior alongside implementation
- **Framework**: pytest (existing)
- **Verification method**: pytest for code changes (Task 5) + agent-executed QA scenarios for all tasks (SVGs, docs, config, code)

### QA Policy
Every task includes agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

**Environment prerequisite**: `.venv/` exists from Phase 1 (Python 3.14.3, all dev deps installed). Activate with `source .venv/bin/activate` before running pytest or importing project modules.

- **SVG files**: Bash (Python XML parsing) — validate well-formed XML, check accessibility attributes, verify file size
- **Markdown**: Bash (grep/python) — verify section ordering, pin number consistency, image references
- **Code/Tests**: Bash (pytest) — verify single-pin toggle behavior and backward compatibility
- **Cross-validation**: Bash (python) — compare pin numbers across config YAML, hardware guide, and SVGs

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — SVG diagrams + code change in parallel):
├── Task 1: Create 6532 RIOT socket SVG diagram [artistry]
├── Task 2: Create RPi GPIO header SVG diagram [artistry]
├── Task 3: Create Atari-to-Pi wiring SVG diagram [artistry]
└── Task 5: Add single-pin toggle support to gpio_monitor.py + update tests [deep]

Wave 2 (After Wave 1 — config update depends on Task 5, markdown needs SVGs + config):
├── Task 6: Update config/switches.example.yaml to single-pin toggle config [quick]
└── Task 4: Rewrite docs/hardware-guide.md [writing] (depends on Tasks 1-3, 5-6)

Wave FINAL (After ALL tasks — verification):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 4 | 1 |
| 2 | — | 4 | 1 |
| 3 | — | 4 | 1 |
| 5 | — | 6, 4 | 1 |
| 6 | 5 | 4 | 2 |
| 4 | 1, 2, 3, 5, 6 | F1-F4 | 2 |
| F1-F4 | 4 | — | FINAL |

### Agent Dispatch Summary

- **Wave 1**: **4 tasks** — T1 → `artistry`, T2 → `artistry`, T3 → `artistry`, T5 → `deep`
- **Wave 2**: **2 tasks** — T6 → `quick`, T4 → `writing` (T6 can start as soon as T5 done; T4 waits for all)
- **FINAL**: **4 tasks** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Create 6532 RIOT 40-Pin DIP Socket SVG Diagram

  **What to do**:
  - Create `docs/diagrams/6532-riot-socket.svg` — a hand-coded SVG showing the 40-pin DIP socket pinout of the 6532 RIOT (A202) chip
  - Show all 40 pins with standard DIP counter-clockwise numbering (Pin 1 top-left, Pin 20 bottom-left, Pin 21 bottom-right, Pin 40 top-right)
  - Highlight the 5 switch-related pins with a distinct color (gold/yellow):
    - Pin 24 → GAME RESET
    - Pin 23 → GAME SELECT
    - Pin 21 → B/W-COLOR
    - Pin 17 → DIFFICULTY LEFT (Player 1)
    - Pin 16 → DIFFICULTY RIGHT (Player 2)
  - Highlight Pin 1 (VSS/GND) in dark gray as the common ground connection point
  - Mark unused pins in a muted/light color
  - Include a notch indicator at the top of the DIP package and a Pin 1 dot marker
  - Label each highlighted pin with BOTH its pin number AND signal name (e.g., "Pin 24 — RESET")
  - Add a chip label in the center: "6532 RIOT (A202)"
  - Include SVG accessibility: `role="img"`, `aria-labelledby`, `<title>6532 RIOT 40-Pin DIP Socket Pinout</title>`, `<desc>Pinout diagram of the MOS 6532 RIOT chip showing which socket pins connect to Atari 2600 console switches</desc>`
  - Target viewBox: `0 0 520 680` (tall rectangle for DIP-40)
  - Keep file size under 20KB — no embedded raster data, no external references, no `<script>`, no `<foreignObject>`
  - Create the `docs/diagrams/` directory if it doesn't exist

  **Must NOT do**:
  - No inline SVG in any markdown file
  - No Mermaid diagrams
  - No embedded images or external dependencies
  - No animated elements
  - Do not modify any non-docs files

  **Recommended Agent Profile**:
  - **Category**: `artistry`
    - Reason: Hand-coding an SVG diagram requires creative visual design within technical constraints — precise geometry, color choices, label placement, and accessibility compliance
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: SVG creation doesn't involve UI components or browser rendering

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Task 4 (markdown rewrite needs SVG files to reference)
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL):

  **Pattern References**:
  - No existing SVG files in the repo to follow — this is the first one

  **API/Type References**:
  - `config/switches.example.yaml` — Canonical BCM pin assignments (source of truth for what the Pi side expects)

  **External References**:
  - Atari Field Service Manual (FD100133) pin mapping: Pin 24=RESET, Pin 23=SELECT, Pin 21=B/W-COLOR, Pin 17=DIFF LEFT, Pin 16=DIFF RIGHT, Pin 1=GND
  - Full RIOT pinout from librarian research (see Context section for complete pin list)
  - SVG specification: viewBox, text, rect, circle elements — hand-code using basic SVG primitives
  - GitHub SVG rendering: external .svg files work when referenced via `![alt](path)` — inline SVG is stripped

  **WHY Each Reference Matters**:
  - `switches.example.yaml` — Pin numbers in the SVG must match the software's expectations exactly
  - Atari FSM — The RIOT socket pin numbers are the physical solder point identifiers; errors here could cause incorrect wiring
  - SVG spec — Must be hand-coded with correct geometry for DIP-40 package; no tool-generated bloat

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: SVG is valid well-formed XML
    Tool: Bash
    Preconditions: docs/diagrams/6532-riot-socket.svg exists
    Steps:
      1. Run: python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/diagrams/6532-riot-socket.svg'); print('VALID')"
      2. Assert exit code 0 and output contains "VALID"
    Expected Result: Exit code 0, output "VALID"
    Failure Indicators: ParseError exception, non-zero exit code
    Evidence: .sisyphus/evidence/task-1-svg-valid.txt

  Scenario: SVG has accessibility attributes
    Tool: Bash (grep)
    Preconditions: docs/diagrams/6532-riot-socket.svg exists
    Steps:
      1. grep 'role="img"' docs/diagrams/6532-riot-socket.svg
      2. grep '<title' docs/diagrams/6532-riot-socket.svg
      3. grep '<desc' docs/diagrams/6532-riot-socket.svg
    Expected Result: All three greps return matches (exit code 0)
    Failure Indicators: Any grep returns no match (exit code 1)
    Evidence: .sisyphus/evidence/task-1-svg-accessibility.txt

  Scenario: SVG contains correct switch pin labels
    Tool: Bash (grep)
    Preconditions: docs/diagrams/6532-riot-socket.svg exists
    Steps:
      1. grep -i "reset" docs/diagrams/6532-riot-socket.svg (should match pin 24 label)
      2. grep -i "select" docs/diagrams/6532-riot-socket.svg (should match pin 23 label)
      3. grep -i "b.*w\|color\|bw" docs/diagrams/6532-riot-socket.svg (should match pin 21 label)
      4. grep -i "diff.*left\|left.*diff\|player.1\|p1" docs/diagrams/6532-riot-socket.svg (should match pin 17)
      5. grep -i "diff.*right\|right.*diff\|player.2\|p2" docs/diagrams/6532-riot-socket.svg (should match pin 16)
    Expected Result: All five greps return at least one match
    Failure Indicators: Any grep returns no match — missing switch label
    Evidence: .sisyphus/evidence/task-1-svg-labels.txt

  Scenario: SVG file is under 20KB
    Tool: Bash
    Preconditions: docs/diagrams/6532-riot-socket.svg exists
    Steps:
      1. Run: python3 -c "import os; s=os.path.getsize('docs/diagrams/6532-riot-socket.svg'); print(f'{s} bytes'); assert s < 20480, f'Too large: {s}'"
    Expected Result: File size < 20480 bytes
    Failure Indicators: AssertionError with size > 20480
    Evidence: .sisyphus/evidence/task-1-svg-size.txt
  ```

  **Evidence to Capture:**
  - [ ] task-1-svg-valid.txt — XML parse result
  - [ ] task-1-svg-accessibility.txt — Accessibility attribute grep results
  - [ ] task-1-svg-labels.txt — Switch label grep results
  - [ ] task-1-svg-size.txt — File size check

  **Commit**: YES (groups with Tasks 2, 3 — all SVGs in one commit)
  - Message: `docs: add SVG wiring diagrams for Atari-to-Pi connections`
  - Files: `docs/diagrams/6532-riot-socket.svg`
  - Pre-commit: `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/diagrams/6532-riot-socket.svg')"`

- [x] 2. Create Raspberry Pi GPIO Header SVG Diagram

  **What to do**:
  - Create `docs/diagrams/rpi-gpio-header.svg` — a hand-coded SVG showing the Pi 40-pin GPIO header (2×20 grid)
  - Layout: two columns (odd pins left, even pins right), 20 rows, matching the physical Pi header
  - Color code pin types:
    - **3.3V power**: orange (Physical pins 1, 17)
    - **5V power**: red (Physical pins 2, 4)
    - **GND**: dark gray (Physical pins 6, 9, 14, 20, 25, 30, 34, 39)
    - **Project GPIO (in use)**: green with bold labels — the pins actively used after single-pin config migration:
      - BCM 4 (Phys 7) → TV Type (single-pin: Color/B&W from RIOT Pin 21)
      - BCM 6 (Phys 31) → Channel (single-pin)
      - BCM 12 (Phys 32) → Power LED
      - BCM 22 (Phys 15) → Game Select (momentary, from RIOT Pin 23)
      - BCM 23 (Phys 16) → Left Difficulty (single-pin: A/B from RIOT Pin 17)
      - BCM 25 (Phys 22) → Right Difficulty (single-pin: A/B from RIOT Pin 16)
      - BCM 26 (Phys 37) → Power (Shutdown via dtoverlay)
      - BCM 27 (Phys 13) → Game Reset (momentary, from RIOT Pin 24)
    - **Unused GPIO**: light/muted color — all other GPIO pins including BCM 5, 13, 17, 24 (freed by single-pin migration, no longer assigned)
  - Label each project GPIO pin with its switch function (active pins only):
    - BCM 4 → TV Type
    - BCM 6 → Channel
    - BCM 12 → Power LED
    - BCM 22 → Game Select
    - BCM 23 → Left Difficulty
    - BCM 25 → Right Difficulty
    - BCM 26 → Power (Shutdown)
    - BCM 27 → Game Reset
  - Freed pins (BCM 5, 13, 17, 24) should be rendered in the muted/unused color WITHOUT switch function labels — they are no longer part of the active config
  - Show both BCM number and physical pin number for each pin
  - Include SVG accessibility: `role="img"`, `aria-labelledby`, `<title>Raspberry Pi GPIO Header Pin Assignments</title>`, `<desc>Diagram of the Raspberry Pi 40-pin GPIO header showing which pins are used for Atari 2600 switch connections and power LED</desc>`
  - Target viewBox: `0 0 700 640`
  - Keep under 20KB, no external deps, no script, no foreignObject

  **Must NOT do**:
  - No inline SVG in markdown
  - No pin assignments that differ from `config/switches.example.yaml`
  - Do not modify any non-docs files

  **Recommended Agent Profile**:
  - **Category**: `artistry`
    - Reason: Visual design of a pin-grid diagram with color coding and label placement requires creative problem-solving
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Task 4
  - **Blocked By**: None

  **References** (CRITICAL):

  **Pattern References**:
  - `config/switches.example.yaml` — CANONICAL source of truth for all BCM pin assignments. Every pin number in this SVG MUST match this file exactly.

  **API/Type References**:
  - Raspberry Pi 3B+ GPIO header physical pinout — standard 2×20 pin layout

  **External References**:
  - RPi GPIO pinout reference: https://pinout.xyz — for physical pin ↔ BCM mapping verification
  - `config/switches.example.yaml:1-57` — All pin assignments: power=26, tv_type=4/17, game_select=22, game_reset=27, difficulty_left=23/24, difficulty_right=25/5, channel=6/13, power_led=12

  **WHY Each Reference Matters**:
  - `switches.example.yaml` — Single source of truth. If this SVG shows a different BCM pin than the config, the user will wire incorrectly.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: SVG is valid well-formed XML
    Tool: Bash
    Preconditions: docs/diagrams/rpi-gpio-header.svg exists
    Steps:
      1. Run: python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/diagrams/rpi-gpio-header.svg'); print('VALID')"
    Expected Result: Exit code 0, "VALID"
    Failure Indicators: ParseError
    Evidence: .sisyphus/evidence/task-2-svg-valid.txt

  Scenario: SVG contains all active project BCM pin numbers
    Tool: Bash
    Preconditions: docs/diagrams/rpi-gpio-header.svg exists
    Steps:
      1. For each active project BCM pin [4, 6, 12, 22, 23, 25, 26, 27], grep the SVG
      2. Run: python3 -c "import re; c=open('docs/diagrams/rpi-gpio-header.svg').read(); pins=[4,6,12,22,23,25,26,27]; found=[p for p in pins if re.search(rf'\b{p}\b', c)]; print(f'Found {len(found)}/8 active pins: {found}'); assert len(found)==8, f'Missing: {set(pins)-set(found)}'"
    Expected Result: All 8 active project BCM pins present with labels
    Failure Indicators: Any active pin missing from SVG content
    Evidence: .sisyphus/evidence/task-2-svg-pins.txt

  Scenario: SVG has accessibility attributes
    Tool: Bash (grep)
    Steps:
      1. grep 'role="img"' docs/diagrams/rpi-gpio-header.svg
      2. grep '<title' docs/diagrams/rpi-gpio-header.svg
      3. grep '<desc' docs/diagrams/rpi-gpio-header.svg
    Expected Result: All three present
    Evidence: .sisyphus/evidence/task-2-svg-accessibility.txt

  Scenario: SVG file under 20KB
    Tool: Bash
    Steps:
      1. python3 -c "import os; s=os.path.getsize('docs/diagrams/rpi-gpio-header.svg'); print(f'{s} bytes'); assert s < 20480"
    Expected Result: < 20480 bytes
    Evidence: .sisyphus/evidence/task-2-svg-size.txt
  ```

  **Evidence to Capture:**
  - [ ] task-2-svg-valid.txt
  - [ ] task-2-svg-pins.txt
  - [ ] task-2-svg-accessibility.txt
  - [ ] task-2-svg-size.txt

  **Commit**: YES (groups with Tasks 1, 3)
  - Message: `docs: add SVG wiring diagrams for Atari-to-Pi connections`
  - Files: `docs/diagrams/rpi-gpio-header.svg`

- [x] 3. Create Atari-to-Pi Full Wiring Connection SVG Diagram

  **What to do**:
  - Create `docs/diagrams/atari-to-pi-wiring.svg` — a hand-coded SVG showing the complete wiring between the RIOT IC socket and the Pi GPIO header
  - Landscape layout: RIOT socket simplified view on the left, Pi GPIO header simplified view on the right
  - **USER DECISION: IC socket only approach** — All switches wired through RIOT IC socket pads with single-pin-per-switch config. The daemon config will be updated to use single-pin toggle detection instead of dual-pin.
  - Draw color-coded connection lines between corresponding pins (ONE wire per switch, not two):
    - RIOT Pin 24 (RESET) → Pi BCM 27 (Physical 13) — Game Reset
    - RIOT Pin 23 (SELECT) → Pi BCM 22 (Physical 15) — Game Select
    - RIOT Pin 21 (B/W-COLOR) → Pi BCM 4 (Physical 7) — TV Type toggle (single pin: LOW=B&W, HIGH=Color)
    - RIOT Pin 17 (DIFF LEFT) → Pi BCM 23 (Physical 16) — Left Difficulty toggle (single pin: LOW=B, HIGH=A)
    - RIOT Pin 16 (DIFF RIGHT) → Pi BCM 25 (Physical 22) — Right Difficulty toggle (single pin: LOW=B, HIGH=A)
  - Show ground bus as a thick black/dark line: RIOT Pin 1 (GND) → Pi GND (any GND pin, e.g., Physical 6)
  - Note on diagram: Power switch (BCM 26) and Channel switch (BCM 6/13) are NOT on the main board IC sockets — they wire directly to their respective switch contacts
  - Label each connection line with the switch name
  - Add a legend showing color coding
  - Include SVG accessibility attributes
  - Target viewBox: `0 0 1200 500` (wide landscape)
  - Keep under 20KB

  **Must NOT do**:
  - No inline SVG
  - No animated elements
  - No embedded raster data
  - Do not modify non-docs files

  **Recommended Agent Profile**:
  - **Category**: `artistry`
    - Reason: Most complex SVG — requires creative layout of two endpoint diagrams with connecting wires, color coding, and legends. Visual clarity under space constraints.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 4
  - **Blocked By**: None

  **References** (CRITICAL):

  **Pattern References**:
  - `config/switches.example.yaml:1-57` — Current pin assignments. NOTE: The config will be changed to single-pin toggle detection as part of Task 4 (documented config update in the guide). The wiring diagram should show the NEW simplified pin mapping.
  - `retropie2600/gpio_monitor.py` — `_get_pins_for_switch()` method shows how pin keys map to position names; `read_all_states()` shows how toggle positions are detected (first pin reading LOW wins). The single-pin approach uses "pin" key with level detection for toggle position.

  **API/Type References**:
  - `config/switches.example.yaml` — Will be updated to single-pin config for toggles. Each toggle gets ONE GPIO pin instead of two.

  **External References**:
  - Atari FSM RIOT pin mapping: Pin 24=RESET, Pin 23=SELECT, Pin 21=B/W, Pin 17=DIFF-L, Pin 16=DIFF-R, Pin 1=GND
  - Each RIOT pin is a single digital signal: switch grounds the line (LOW) in one position, leaves it pulled HIGH in the other

  **WHY Each Reference Matters**:
  - `switches.example.yaml` — Defines the Pi GPIO endpoints. With the single-pin approach, fewer wires are needed — the diagram is simpler and clearer.
  - `gpio_monitor.py` — Confirms active-low logic. Toggle position is determined by level (LOW=one position, HIGH=other) on a single pin.
  - The wiring diagram is the most critical visual — an error here means incorrect physical wiring.

  **NOTE FOR EXECUTOR**: User decided on IC-socket-only approach. All 5 console switches wire through the RIOT socket with ONE wire per switch. Toggle position (A/B, Color/BW) is determined by HIGH/LOW level on the single pin. The daemon config will be updated to use single-pin detection. Show ONLY the IC socket approach in this diagram — no dual-approach complexity.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: SVG is valid well-formed XML
    Tool: Bash
    Preconditions: docs/diagrams/atari-to-pi-wiring.svg exists
    Steps:
      1. Run: python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/diagrams/atari-to-pi-wiring.svg'); print('VALID')"
    Expected Result: Exit code 0, "VALID"
    Evidence: .sisyphus/evidence/task-3-svg-valid.txt

  Scenario: SVG references both RIOT pins and Pi BCM pins
    Tool: Bash
    Preconditions: docs/diagrams/atari-to-pi-wiring.svg exists
    Steps:
      1. Verify RIOT pins: grep for "24" (RESET), "23" (SELECT), "21" (B/W), "17" (DIFF-L), "16" (DIFF-R)
      2. Verify Pi BCM pins used in single-pin wiring: grep for BCM numbers [4, 22, 23, 25, 27]
      3. Run: python3 -c "c=open('docs/diagrams/atari-to-pi-wiring.svg').read(); riot=['24','23','21','17','16']; bcm=['4','22','23','25','27']; riot_found=[p for p in riot if p in c]; bcm_found=[p for p in bcm if p in c]; print(f'RIOT pins: {len(riot_found)}/5 {riot_found}'); print(f'BCM pins: {len(bcm_found)}/5 {bcm_found}'); assert len(riot_found)>=4, f'Missing RIOT pins'; assert len(bcm_found)>=4, f'Missing BCM pins'; print('Pin references OK')"
    Expected Result: At least 4/5 RIOT pins and 4/5 BCM pins present (allowing for formatting variation)
    Evidence: .sisyphus/evidence/task-3-svg-pins.txt

  Scenario: SVG has accessibility attributes
    Tool: Bash (grep)
    Steps:
      1. grep 'role="img"' docs/diagrams/atari-to-pi-wiring.svg
      2. grep '<title' docs/diagrams/atari-to-pi-wiring.svg
      3. grep '<desc' docs/diagrams/atari-to-pi-wiring.svg
    Expected Result: All three present
    Evidence: .sisyphus/evidence/task-3-svg-accessibility.txt

  Scenario: SVG file under 20KB
    Tool: Bash
    Steps:
      1. python3 -c "import os; s=os.path.getsize('docs/diagrams/atari-to-pi-wiring.svg'); print(f'{s} bytes'); assert s < 20480"
    Expected Result: < 20480 bytes
    Evidence: .sisyphus/evidence/task-3-svg-size.txt
  ```

  **Evidence to Capture:**
  - [ ] task-3-svg-valid.txt
  - [ ] task-3-svg-accessibility.txt
  - [ ] task-3-svg-pins.txt
  - [ ] task-3-svg-size.txt

  **Commit**: YES (groups with Tasks 1, 2)
  - Message: `docs: add SVG wiring diagrams for Atari-to-Pi connections`
  - Files: `docs/diagrams/atari-to-pi-wiring.svg`

- [x] 4. Rewrite `docs/hardware-guide.md` with IC Socket Wiring Instructions and Embedded Diagrams

  **What to do**:
  Rewrite the existing hardware guide (~133 lines → ~350+ lines) to incorporate IC socket wiring details, embed the SVG diagrams, and add comprehensive step-by-step instructions. The rewrite must PRESERVE all existing good content while ENHANCING it significantly.

  **Document structure** (sections in this order):

  1. **Title + Introduction** — What this guide covers, that ICs have been removed, overview of approach
  2. **⚠️ Safety Warnings** — MOVE to top. Include the existing ESD/power-off/wire-routing warnings PLUS the NEW 5V overvoltage warning as a prominent callout
  3. **Bill of Materials** — Preserve existing BOM table, add "28 AWG hookup wire or wire-wrap wire" for IC socket pad soldering
  4. **Understanding the Atari 2600 Board** — NEW section explaining:
     - What the 6532 RIOT chip was and why its socket is the wiring access point
     - Where the A202 (RIOT) socket is on the CX-2600A board (topmost chip socket, closest to switches)
     - How to identify Pin 1 (notch/dot on socket body)
     - DIP-40 numbering convention (counter-clockwise from Pin 1)
     - Brief DPDT switch explanation — why switches have 6 pins but the IC socket pad gives a single signal
     - Embed `![6532 RIOT Socket Pinout](diagrams/6532-riot-socket.svg)`
  5. **⚠️ Voltage Mitigation — MUST DO BEFORE WIRING** — NEW section:
     - Explain the 24KΩ pull-up resistors on the Atari board pull switch lines to 5V
     - 5V exceeds Pi's 3.3V GPIO tolerance — will damage the Pi
     - **Recommended approach**: Desolder/remove the 24KΩ pull-up resistors (R218, R219, R220, etc.) from the board. The Pi's internal pull-ups (~50KΩ) will hold lines at safe 3.3V.
     - **Alternative 1**: Voltage divider (2× 10KΩ resistors per line) — 5V → 2.5V
     - **Alternative 2**: Level shifter (74HCT245 or similar)
     - How to verify with multimeter: measure voltage on each RIOT socket pin with power disconnected and after mitigation
  6. **IC Socket Pin Reference** — NEW section:
     - Master mapping table: Switch Name | RIOT Socket Pin | Signal Description | Logic Level
     - Include ALL 5 switches: RESET (Pin 24), SELECT (Pin 23), B/W-COLOR (Pin 21), DIFF LEFT (Pin 17), DIFF RIGHT (Pin 16)
     - Note that POWER and CHANNEL switches do NOT connect to IC sockets
     - Reference to original schematic: `![Atari 2600 CX-2600A Schematic (Sheet 2 — Main Board)](Schematic_Atari2600A_2000.png)`
  7. **GPIO Pin Assignment Table** — UPDATE the existing table to reflect the simplified single-pin config. Fewer pins needed since each toggle uses one GPIO pin instead of two. Show BCM pin, physical pin, switch name, type, and Stella key/function.
     - Embed `![Raspberry Pi GPIO Header](diagrams/rpi-gpio-header.svg)`
  8. **IC Socket Wiring Approach** — NEW section explaining:
     - **USER DECISION: All switches wire through RIOT IC socket pads** — single wire per switch, single-pin config
     - Each toggle switch has ONE RIOT pin: HIGH = one position, LOW = other position
     - This simplifies wiring to just 5 signal wires + 1 ground wire from the RIOT socket
     - The daemon config uses single-pin detection: `pin:` key instead of `pin_a:/pin_b:` for toggles
     - Note: POWER and CHANNEL switches don't connect to RIOT — see their subsections for direct wiring
     - Include updated `switches.example.yaml` snippet showing single-pin toggle config
  9. **Step-by-Step Wiring Instructions** — NEW section with per-switch subsections:
     - **Game Reset** (momentary): RIOT Pin 24 → Pi BCM 27 (Physical 13), RIOT Pin 1 (GND) → Pi GND
     - **Game Select** (momentary): RIOT Pin 23 → Pi BCM 22 (Physical 15), common GND
     - **TV Type / B&W-Color** (toggle, single pin): RIOT Pin 21 → Pi BCM 4 (Physical 7). LOW=B&W (triggers F4), HIGH=Color (triggers F3)
     - **Difficulty Left** (toggle, single pin): RIOT Pin 17 → Pi BCM 23 (Physical 16). LOW=B/Novice (triggers F6), HIGH=A/Pro (triggers F5)
     - **Difficulty Right** (toggle, single pin): RIOT Pin 16 → Pi BCM 25 (Physical 22). LOW=B/Novice (triggers F8), HIGH=A/Pro (triggers F7)
     - **Channel** (toggle): Wire directly to switch contacts (NOT on main board near IC sockets). Pin for position detection.
     - **Power** (toggle): BCM 26 via `gpio-shutdown` dtoverlay — wire directly to power switch contacts
     - Each subsection includes: connection table (source → destination), wire color suggestion, multimeter verification step
     - Embed `![Full Wiring Diagram](diagrams/atari-to-pi-wiring.svg)`
  10. **Pull-Up Resistor Notes** — PRESERVE and enhance existing section. Explain Pi internal PUD_UP at 3.3V. Note that if board pull-ups are removed (Section 5), Pi pull-ups handle everything.
  11. **Power LED Installation** — PRESERVE existing content verbatim
  12. **Fan Installation** — PRESERVE existing content verbatim
  13. **Port Cutout Guide** — PRESERVE existing content verbatim
  14. **/boot/config.txt Configuration** — PRESERVE existing content
  15. **Testing Your Wiring** — PRESERVE and enhance. Add expected log output examples for each switch type (SwitchEvent format). Add example journalctl output showing toggle position changes and momentary press/release.
  16. **Troubleshooting** — NEW section:
      - "Pin reads HIGH all the time" → check GND connection, verify switch contacts
      - "Pin reads LOW all the time" → floating pin, check pull-up resistor / Pi PUD_UP config
      - "Both toggle positions read the same" → wrong switch pad wired; use multimeter continuity
      - "5V detected on GPIO pin" → STOP — pull-up resistors not removed; see Section 5
      - "No events in daemon log" → verify pin numbers match config, check pigpio daemon running
  17. **References** — NEW section linking to:
      - Atari FSM (FD100133)
      - DJSures Arduino IC socket project
      - etheling/rpie2600
      - MOS 6532 RIOT datasheet

  **Must NOT do**:
  - No inline SVG (use `![alt](path)` references only)
  - Do not modify any .py, .yaml, .service, or test files (those are handled by Tasks 5 and 6)
  - Do not invent new pin assignments — MUST match the updated `config/switches.example.yaml` (single-pin format)
  - Do not remove existing content that is correct — enhance and reorganize
  - No Mermaid diagrams

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: Primary deliverable is a long-form technical document (~350+ lines of markdown). Requires clear prose, table formatting, section organization, and integration of technical details into readable instructions.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No UI work involved

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (sequential after Wave 1)
  - **Blocks**: F1-F4
  - **Blocked By**: Tasks 1, 2, 3 (needs SVG files to exist for referencing)

  **References** (CRITICAL):

  **Pattern References**:
  - `docs/hardware-guide.md:1-133` — Current guide content to preserve and enhance. Specifically preserve: BOM table (lines 9-23), GPIO pin table (lines 29-44), Power LED section (lines 70-74), Fan section (lines 78-83), Port Cutout section (lines 88-93), Safety warnings (lines 96-104), /boot/config.txt (lines 108-119), Testing section (lines 124-133)
  - `config/switches.example.yaml:1-57` — Source of truth for ALL pin assignments. Every BCM pin number in the guide MUST match this file.

  **API/Type References**:
  - `retropie2600/gpio_monitor.py` — Switch type handling (toggle vs momentary), pin key mapping (_get_pins_for_switch), active-low detection (level==0), event format (SwitchEvent with switch_name, position, timestamp)
  - `retropie2600/config.py` — Config validation: BCM 0-27 valid range, reserved pins {0,1,2,3,7,8,9,10,11,14,15}, duplicate detection

  **External References**:
  - Atari FSM pin mapping: RIOT Pin 24=RESET, 23=SELECT, 21=B/W, 17=DIFF-L, 16=DIFF-R, 1=GND
  - DJSures project: https://github.com/DJSures/Atari-2600-VCS-USB-Joystick-Console-Arduino — confirms IC socket pad approach
  - etheling/rpie2600: https://github.com/etheling/rpie2600 — alternative Pi mod reference
  - Atari FSM: https://vtda.org/docs/computing/Atari/FD100133_Atari2600FieldServiceManualRev02_Jan83.pdf
  - MOS 6532 RIOT datasheet: http://www.6502.org/documents/datasheets/mos/mos_6532_riot.pdf

  **WHY Each Reference Matters**:
  - `hardware-guide.md` — Must know exactly what content exists to preserve vs replace. The BOM, pin table, LED/fan/port sections are good and should stay.
  - `switches.example.yaml` — Every pin number must be verified against this file. A discrepancy means the documentation will lead to incorrect wiring.
  - `gpio_monitor.py` — Explains what happens when a switch event fires. The testing section needs to show what log output to expect, which requires understanding the event format.
  - `config.py` — The troubleshooting section should mention reserved pins and valid BCM range so users don't pick invalid pins.
  - Atari FSM — Primary authority for RIOT socket pin numbers. These are the physical locations the user will solder to.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Guide has rich table content
    Tool: Bash
    Preconditions: docs/hardware-guide.md exists
    Steps:
      1. Run: python3 -c "import re; c=open('docs/hardware-guide.md').read(); t=re.findall(r'\|.*\|', c); print(f'{len(t)} table rows'); assert len(t) > 20, f'Only {len(t)} rows'"
    Expected Result: More than 20 table rows (BOM + GPIO + RIOT mapping + connection tables)
    Failure Indicators: Fewer than 20 table rows
    Evidence: .sisyphus/evidence/task-4-table-count.txt

  Scenario: All three SVG files are referenced
    Tool: Bash (grep)
    Preconditions: docs/hardware-guide.md exists
    Steps:
      1. grep '6532-riot-socket.svg' docs/hardware-guide.md
      2. grep 'rpi-gpio-header.svg' docs/hardware-guide.md
      3. grep 'atari-to-pi-wiring.svg' docs/hardware-guide.md
    Expected Result: All three filenames found (three exit code 0s)
    Failure Indicators: Any grep returns empty
    Evidence: .sisyphus/evidence/task-4-svg-refs.txt

  Scenario: Schematic PNG is referenced
    Tool: Bash (grep)
    Preconditions: docs/hardware-guide.md exists
    Steps:
      1. grep 'Schematic_Atari2600A_2000.png' docs/hardware-guide.md
    Expected Result: At least one match
    Evidence: .sisyphus/evidence/task-4-schematic-ref.txt

  Scenario: No inline SVG in markdown
    Tool: Bash (grep)
    Preconditions: docs/hardware-guide.md exists
    Steps:
      1. grep '<svg' docs/hardware-guide.md || echo "PASS: no inline SVG"
    Expected Result: No matches (grep exit code 1), "PASS" output
    Failure Indicators: Any match found — inline SVG present
    Evidence: .sisyphus/evidence/task-4-no-inline-svg.txt

  Scenario: 5V warning appears before wiring instructions
    Tool: Bash
    Preconditions: docs/hardware-guide.md exists
    Steps:
      1. Run: python3 -c "c=open('docs/hardware-guide.md').read(); w=c.lower().index('5v'); s=c.lower().index('step-by-step'); assert w < s, f'5V at {w}, Step-by-Step at {s}'; print(f'5V warning at char {w}, wiring at {s} — correct order')"
    Expected Result: 5V warning position < step-by-step wiring position
    Failure Indicators: AssertionError showing wrong order
    Evidence: .sisyphus/evidence/task-4-section-order.txt

  Scenario: All BCM pins from config appear in guide
    Tool: Bash
    Preconditions: docs/hardware-guide.md and config/switches.example.yaml exist
    Steps:
      1. Run: python3 -c "
         import re
         config = open('config/switches.example.yaml').read()
         guide = open('docs/hardware-guide.md').read()
         config_pins = set(re.findall(r'pin\w*:\s*(\d+)', config))
         missing = [p for p in config_pins if p not in guide]
         print(f'Config pins: {sorted(config_pins)}')
         print(f'Missing from guide: {missing}')
         assert not missing, f'Missing pins: {missing}'
         print('All config pins found in guide')
         "
    Expected Result: All config pin numbers found in the guide text
    Failure Indicators: Any pin number missing
    Evidence: .sisyphus/evidence/task-4-pin-consistency.txt

  Scenario: Existing content preserved — key sections present
    Tool: Bash (grep)
    Preconditions: docs/hardware-guide.md exists
    Steps:
      1. grep -i "bill of materials\|BOM" docs/hardware-guide.md
      2. grep -i "power led" docs/hardware-guide.md
      3. grep -i "fan installation\|fan" docs/hardware-guide.md
      4. grep -i "port cutout" docs/hardware-guide.md
      5. grep -i "boot/config.txt\|config.txt" docs/hardware-guide.md
      6. grep -i "testing your wiring\|testing" docs/hardware-guide.md
      7. grep -i "troubleshooting" docs/hardware-guide.md
    Expected Result: All seven greps return matches
    Failure Indicators: Any section heading missing
    Evidence: .sisyphus/evidence/task-4-sections-preserved.txt

  Scenario: Task 4 only modifies docs files (not code or config)
    Tool: Bash
    Preconditions: Working directory is the repo root, previous tasks already committed
    Steps:
      1. Run: git diff --name-only HEAD | grep -v '^docs/' | grep -v '.sisyphus/' || echo "PASS: only docs changed in this task"
    Expected Result: Empty output or "PASS" (Task 4's uncommitted changes are only in docs/)
    Failure Indicators: Any non-docs file path in output (would mean Task 4 touched code/config files it shouldn't have)
    Evidence: .sisyphus/evidence/task-4-scope-check.txt
  ```

  **Evidence to Capture:**
  - [ ] task-4-table-count.txt
  - [ ] task-4-svg-refs.txt
  - [ ] task-4-schematic-ref.txt
  - [ ] task-4-no-inline-svg.txt
  - [ ] task-4-section-order.txt
  - [ ] task-4-pin-consistency.txt
  - [ ] task-4-sections-preserved.txt
  - [ ] task-4-scope-check.txt

  **Commit**: YES
  - Message: `docs: rewrite hardware guide with IC socket wiring instructions`
  - Files: `docs/hardware-guide.md`
  - Pre-commit: `python3 -c "c=open('docs/hardware-guide.md').read(); assert '5V' in c; assert 'RIOT' in c; assert '.svg' in c; print('Pre-commit checks pass')"`

- [x] 5. Add Single-Pin Toggle Support to `gpio_monitor.py` + Update Tests

  **What to do**:
  The IC socket wiring approach means each toggle switch has ONE GPIO pin instead of two. Currently, `_get_pins_for_switch()` maps a single `pin:` key to position `"pressed"` — which is wrong for toggles. We need single-pin toggles to report meaningful position names based on pin level.

  **Implementation approach**:
  - Add new config keys for single-pin toggles. For each toggle switch that uses single-pin detection, the config should specify a `pin:` key plus `positions:` mapping that defines what LOW and HIGH mean:
    ```yaml
    tv_type:
      pin: 4
      type: toggle
      positions:
        low: "bw"      # LOW level = B&W position
        high: "color"   # HIGH level = Color position
    ```
  - Update `_get_pins_for_switch()` to handle the single-pin toggle case:
    - If a toggle switch has `pin:` AND `positions:`, it's a single-pin toggle
    - The `positions.low` value is the position name for level==0
    - The `positions.high` value is the position name for level!=0
  - Update `_make_edge_handler()` for single-pin toggles:
    - For `SwitchType.TOGGLE` with single-pin config: fire events for BOTH level==0 AND level!=0 (not just level==0 as current)
    - Use the `positions` mapping to determine the position name
  - The dual-pin approach (pin_a/pin_b, pin_color/pin_bw) MUST continue to work unchanged for backward compatibility
  - Update `read_all_states()` to handle single-pin toggles correctly (read level, map to position via `positions` dict)

  **Key constraint**: The existing dual-pin toggle behavior (pin_a/pin_b firing only on level==0) must NOT change. The single-pin behavior is additive.

  **Tests to write/update**:
  - Test single-pin toggle fires event on LOW with position from `positions.low`
  - Test single-pin toggle fires event on HIGH with position from `positions.high`
  - Test `read_all_states()` returns correct position for single-pin toggle based on current pin level
  - Test backward compatibility: dual-pin toggle (pin_a/pin_b) still works as before
  - Test config validation accepts `positions:` key with `low:` and `high:` subkeys

  **Must NOT do**:
  - Do not break existing dual-pin toggle behavior
  - Do not change momentary switch behavior
  - Do not change daemon.py event routing — it already handles `{switch_name}_{position}` generically
  - Do not change the power switch handling

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires careful modification of GPIO monitor logic with backward compatibility constraints. Must understand edge handler semantics, position naming, and both pin detection modes.
  - **Skills**: [`test-driven-development`]
    - `test-driven-development`: Write tests first for single-pin toggle behavior, then implement

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3)
  - **Blocks**: Tasks 4, 6
  - **Blocked By**: None

  **References** (CRITICAL):

  **Pattern References**:
  - `retropie2600/gpio_monitor.py:105-124` — `_get_pins_for_switch()` — current pin key mapping. Add single-pin toggle handling here.
  - `retropie2600/gpio_monitor.py:126-150` — `_make_edge_handler()` — current edge handler. Toggle branch (line 138-140) ignores level!=0. Single-pin toggles need to fire on both levels.
  - `retropie2600/gpio_monitor.py:84-103` — `read_all_states()` — reads pin levels for startup sync. Needs to handle single-pin toggles.

  **Test References**:
  - `tests/` directory — find existing toggle switch tests and follow the same mocking patterns for pigpio

  **API/Type References**:
  - `retropie2600/config.py` — Config validation. May need to accept `positions:` key without treating it as a pin number.

  **WHY Each Reference Matters**:
  - `gpio_monitor.py` — This IS the file being modified. Every function needs to be understood to avoid regressions.
  - Existing tests — Must follow the same mock patterns to ensure consistent test quality.
  - `config.py` — Validation logic scans for keys containing "pin" and validates them as BCM numbers. The new `positions:` key must not be caught by this validation.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Single-pin toggle fires event on LOW with correct position
    Tool: Bash (pytest)
    Preconditions: Test written for single-pin toggle
    Steps:
      1. Run: source .venv/bin/activate && python -m pytest tests/ -v -k "single_pin" --no-header 2>&1
    Expected Result: All single-pin toggle tests pass
    Failure Indicators: Any test failure
    Evidence: .sisyphus/evidence/task-5-single-pin-tests.txt

  Scenario: Existing dual-pin toggle tests still pass (backward compat)
    Tool: Bash (pytest)
    Preconditions: No breaking changes to dual-pin behavior
    Steps:
      1. Run: source .venv/bin/activate && python -m pytest tests/ -v --no-header 2>&1
    Expected Result: All 62+ tests pass (existing + new)
    Failure Indicators: Any previously-passing test fails
    Evidence: .sisyphus/evidence/task-5-all-tests.txt

  Scenario: Config validation accepts positions key without treating it as pin
    Tool: Bash (pytest)
    Preconditions: Config validation updated
    Steps:
      1. Run: source .venv/bin/activate && python -m pytest tests/ -v -k "config" --no-header 2>&1
    Expected Result: All config validation tests pass
    Failure Indicators: ConfigError raised for valid positions config
    Evidence: .sisyphus/evidence/task-5-config-tests.txt
  ```

  **Evidence to Capture:**
  - [ ] task-5-single-pin-tests.txt
  - [ ] task-5-all-tests.txt
  - [ ] task-5-config-tests.txt

  **Commit**: YES
  - Message: `feat(gpio): add single-pin toggle detection for IC socket wiring`
  - Files: `retropie2600/gpio_monitor.py`, `retropie2600/config.py` (if needed), `tests/test_gpio_monitor.py`, `tests/test_config.py` (if needed)
  - Pre-commit: `source .venv/bin/activate && python -m pytest tests/ -v --no-header`

- [x] 6. Update `config/switches.example.yaml` to Single-Pin Toggle Config

  **What to do**:
  Update the example config to use single-pin toggle detection for switches that wire through the RIOT IC socket. This matches the IC-socket-only wiring approach.

  **Changes**:
  ```yaml
  # BEFORE (dual-pin):
  tv_type:
    pin_color: 4
    pin_bw: 17
    type: toggle

  # AFTER (single-pin with positions):
  tv_type:
    pin: 4
    type: toggle
    positions:
      low: "bw"
      high: "color"
  ```

  Apply the same pattern to:
  - `tv_type`: pin: 4, positions: low="bw", high="color"
  - `difficulty_left`: pin: 23, positions: low="b", high="a"
  - `difficulty_right`: pin: 25, positions: low="b", high="a"
  - `channel`: pin: 6, positions: low="3", high="2" (or determine correct mapping from switch orientation)

  Keep unchanged:
  - `power`: pin: 26 (already single-pin, handled by gpio-shutdown)
  - `game_select`: pin: 22 (momentary, already single-pin)
  - `game_reset`: pin: 27 (momentary, already single-pin)
  - `power_led`, `shader`, `shutdown`, `logging` sections

  Update the YAML comments to reference IC socket pin numbers (e.g., "RIOT Pin 21 → BCM 4")

  **Must NOT do**:
  - Do not change momentary switch config (game_select, game_reset)
  - Do not change power switch config
  - Do not change non-switch config sections (shader, shutdown, logging)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple YAML config file update — straightforward key renames with position mappings
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 5 for the positions feature to exist)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 4
  - **Blocked By**: Task 5

  **References** (CRITICAL):

  **Pattern References**:
  - `config/switches.example.yaml:1-57` — Current file to modify
  - Task 5 implementation — defines the `positions:` config schema

  **External References**:
  - Atari FSM: RIOT Pin 21=B/W (LOW=B&W), Pin 17=DIFF-L (LOW=B), Pin 16=DIFF-R (LOW=B)
  - Active-low logic: when switch grounds the RIOT pin → level=0=LOW → "b" or "bw" position

  **WHY Each Reference Matters**:
  - `switches.example.yaml` — This IS the file being modified
  - Atari FSM — Determines which position (A/B, Color/BW) corresponds to LOW vs HIGH

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Updated config is valid YAML
    Tool: Bash
    Steps:
      1. Run: source .venv/bin/activate && python3 -c "import yaml; yaml.safe_load(open('config/switches.example.yaml')); print('Valid YAML')"
    Expected Result: Exit code 0, "Valid YAML"
    Evidence: .sisyphus/evidence/task-6-yaml-valid.txt

  Scenario: Config passes validation
    Tool: Bash
    Steps:
      1. Run: source .venv/bin/activate && python3 -c "from retropie2600.config import Config; c = Config.from_file('config/switches.example.yaml'); print(f'Switches: {list(c.switches.keys())}'); print('Config valid')"
    Expected Result: Config loads without ConfigError, lists all switch names
    Failure Indicators: ConfigError raised
    Evidence: .sisyphus/evidence/task-6-config-valid.txt

  Scenario: All tests still pass with new config
    Tool: Bash
    Steps:
      1. Run: source .venv/bin/activate && python -m pytest tests/ -v --no-header 2>&1
    Expected Result: All tests pass
    Evidence: .sisyphus/evidence/task-6-tests-pass.txt

  Scenario: Toggle switches use single-pin config
    Tool: Bash (grep)
    Steps:
      1. grep "positions:" config/switches.example.yaml
      2. grep "pin_a:" config/switches.example.yaml || echo "PASS: no pin_a (migrated to single-pin)"
      3. grep "pin_color:" config/switches.example.yaml || echo "PASS: no pin_color (migrated to single-pin)"
    Expected Result: "positions:" found, "pin_a:" and "pin_color:" NOT found
    Evidence: .sisyphus/evidence/task-6-single-pin-check.txt
  ```

  **Evidence to Capture:**
  - [ ] task-6-yaml-valid.txt
  - [ ] task-6-config-valid.txt
  - [ ] task-6-tests-pass.txt
  - [ ] task-6-single-pin-check.txt

  **Commit**: YES
  - Message: `config: update switches.example.yaml to single-pin toggle config`
  - Files: `config/switches.example.yaml`
  - Pre-commit: `source .venv/bin/activate && python -m pytest tests/ --no-header`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (grep the guide, check SVG files exist). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in `.sisyphus/evidence/`. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review** — `unspecified-high`
  Validate all 3 SVGs as well-formed XML. Check for accessibility attributes (role="img", title, desc). Verify file sizes < 20KB. Check markdown for broken image references. Verify no inline SVG in markdown. Run all tests (`source .venv/bin/activate && python -m pytest tests/ -v --no-header`) and confirm they pass. Run `git diff --name-only` and confirm only expected files changed: `docs/**`, `config/switches.example.yaml`, `retropie2600/gpio_monitor.py`, `retropie2600/config.py` (if modified), and test files in `tests/`.
  Output: `SVG Valid [N/3] | Accessibility [N/3] | Size [N/3 under 20KB] | Markdown [clean/issues] | Tests [N pass/N fail] | VERDICT`

- [x] F3. **Real Manual QA** — `unspecified-high`
  Open each SVG file and verify pin numbers are correct by cross-referencing against `config/switches.example.yaml` and the Atari FSM pin mappings (RIOT: 24=RESET, 23=SELECT, 21=BW, 17=DIFF-L, 16=DIFF-R). Read the hardware guide top-to-bottom and verify: (a) 5V warning before wiring, (b) all switches have wiring instructions, (c) BCM/physical/RIOT pin numbers are consistent, (d) schematic PNG is referenced.
  Output: `Pin Accuracy [N/N] | Section Order [correct/wrong] | Completeness [N/N switches] | VERDICT`

- [x] F4. **Scope Fidelity Check** — `deep`
  Run `git diff --name-only` and verify ONLY expected files changed: `docs/` files (hardware-guide.md, diagrams/*.svg), `config/switches.example.yaml`, `retropie2600/gpio_monitor.py`, `retropie2600/config.py` (if modified), and test files in `tests/`. Verify NO changes to: `retropie2600/daemon.py`, `docs/installation.md`, `docs/retroarch-setup.md`, `README.md`, any `.service` or `.rules` files. Verify `config/switches.example.yaml` has been updated to single-pin toggle format (no `pin_a:`, `pin_color:` keys; has `positions:` keys). Verify Task 5 code changes match the plan intent (single-pin toggle support additive, dual-pin backward compat preserved).
  Output: `Scope [clean/N violations] | Config Updated [YES/NO] | Unaccounted Files [CLEAN/N] | VERDICT`

---

## Commit Strategy

- **Commit 1** (after Wave 1, Task 5): `feat(gpio): add single-pin toggle detection for IC socket wiring` — `retropie2600/gpio_monitor.py`, `retropie2600/config.py`, test files
- **Commit 2** (after Wave 1, Tasks 1-3): `docs: add SVG wiring diagrams for Atari-to-Pi connections` — `docs/diagrams/*.svg`
- **Commit 3** (after Wave 2, Task 6): `config: update switches.example.yaml to single-pin toggle config` — `config/switches.example.yaml`
- **Commit 4** (after Wave 2, Task 4): `docs: rewrite hardware guide with IC socket wiring instructions` — `docs/hardware-guide.md`

---

## Success Criteria

### Verification Commands
```bash
# AC-1: Markdown has rich table content (20+ table rows)
python3 -c "import re; c=open('docs/hardware-guide.md').read(); t=re.findall(r'\|.*\|', c); print(f'{len(t)} table rows'); assert len(t) > 20"

# AC-2: All SVGs are valid XML
python3 -c "import xml.etree.ElementTree as ET; [ET.parse(f'docs/diagrams/{f}') for f in ['6532-riot-socket.svg', 'rpi-gpio-header.svg', 'atari-to-pi-wiring.svg']]; print('All SVGs valid')"

# AC-3: SVGs have accessibility attributes
grep -l 'role="img"' docs/diagrams/*.svg | wc -l  # Expected: 3
grep -l '<title' docs/diagrams/*.svg | wc -l       # Expected: 3
grep -l '<desc' docs/diagrams/*.svg | wc -l        # Expected: 3

# AC-4: Pin numbers in docs match config (macOS-compatible — no grep -P)
source .venv/bin/activate && python3 -c "
import re
config = open('config/switches.example.yaml').read()
guide = open('docs/hardware-guide.md').read()
config_pins = set(re.findall(r'pin\w*:\s*(\d+)', config))
guide_pins = set(re.findall(r'BCM\s*(\d+)', guide))
print(f'Config pins: {sorted(config_pins)}')
print(f'Guide BCM refs: {sorted(guide_pins)}')
missing = config_pins - guide_pins
assert not missing, f'Config pins missing from guide: {missing}'
print('All config pins found in guide')
"

# AC-5: SVGs referenced in guide
grep -c '6532-riot-socket.svg' docs/hardware-guide.md    # Expected: ≥1
grep -c 'rpi-gpio-header.svg' docs/hardware-guide.md     # Expected: ≥1
grep -c 'atari-to-pi-wiring.svg' docs/hardware-guide.md  # Expected: ≥1

# AC-6: Schematic PNG referenced
grep -c 'Schematic_Atari2600A_2000.png' docs/hardware-guide.md  # Expected: ≥1

# AC-7: No inline SVG in markdown
grep -c '<svg' docs/hardware-guide.md  # Expected: 0

# AC-8: 5V warning before wiring instructions
python3 -c "c=open('docs/hardware-guide.md').read(); assert c.index('5V') < c.index('Step-by-Step')"

# AC-9: SVGs under 20KB
ls -la docs/diagrams/*.svg  # Each < 20480 bytes

# AC-10: All tests pass (including new single-pin toggle tests)
source .venv/bin/activate && python -m pytest tests/ -v --no-header

# AC-11: Config loads successfully with new single-pin format
source .venv/bin/activate && python3 -c "from retropie2600.config import Config; Config.from_file('config/switches.example.yaml'); print('Config valid')"
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All SVGs valid XML with accessibility attributes
- [ ] Pin numbers triple-validated (config YAML, gpio_monitor.py, Atari FSM)
- [ ] 5V warning precedes wiring instructions
- [ ] Existing good content preserved (BOM, safety, config, testing)
- [ ] Single-pin toggle detection works (fires events for both HIGH and LOW)
- [ ] Config updated to single-pin format
- [ ] All tests pass (existing + new)

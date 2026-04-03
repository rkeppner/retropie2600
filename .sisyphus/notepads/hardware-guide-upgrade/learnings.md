# Learnings — hardware-guide-upgrade

## [2026-03-25] Session ses_2ee535174ffeGWmw5BosvOReyo

### Pin Verification (TRIPLE-VALIDATED — DO NOT DOUBT THESE)
All 5 RIOT switch pins confirmed by: Wikipedia SVG (Rockwell R6532 datasheet), Stella Programmer's Guide, continuity testing on the actual board.

| Switch | RIOT Pin | Signal | Logic |
|--------|----------|--------|-------|
| GAME RESET | Pin 24 | PB0 | Momentary: LOW=pressed |
| GAME SELECT | Pin 23 | PB1 | Momentary: LOW=pressed |
| B/W-COLOR | Pin 21 | PB3 | Toggle: LOW=B&W, HIGH=Color |
| LEFT DIFFICULTY | Pin 17 | PB6 | Toggle: LOW=B, HIGH=A |
| RIGHT DIFFICULTY | Pin 16 | PB7 | Toggle: LOW=B, HIGH=A |
| GND | Pin 1 | VSS | Ground reference |

### Physical DIP-40 Layout Key Points
- Pin 1: top-left (marked by notch/dot)
- Pins 1-20: down the LEFT side
- Pins 21-40: up the RIGHT side (Pin 21 is bottom-right, Pin 40 is top-right)
- Pin 20 = VCC (+5V) — bottom-left, DO NOT CONNECT
- Pin 21 = PB3 (B/W-COLOR) — bottom-right, adjacent to VCC on opposite side

### Active Pi GPIO Mapping (single-pin config)
| BCM | Physical | Switch | RIOT Pin |
|-----|----------|--------|----------|
| BCM 27 | Phys 13 | GAME RESET | RIOT Pin 24 |
| BCM 22 | Phys 15 | GAME SELECT | RIOT Pin 23 |
| BCM 4  | Phys 7  | TV TYPE (B/W-Color) | RIOT Pin 21 |
| BCM 23 | Phys 16 | LEFT DIFFICULTY | RIOT Pin 17 |
| BCM 25 | Phys 22 | RIGHT DIFFICULTY | RIOT Pin 16 |
| BCM 26 | Phys 37 | POWER (gpio-shutdown) | direct |
| BCM 6  | Phys 31 | CHANNEL (toggle) | direct |
| BCM 12 | Phys 32 | POWER LED (output) | direct |

### Freed Pins (NOT used in single-pin config)
BCM 5, 13, 17, 24 — show as muted/unused in GPIO SVG, no labels.

### SVG Requirements
- GitHub renders external .svg files (referenced via ![alt](path)) — NOT inline SVG in markdown
- viewBox: RIOT socket 0 0 520 680, Pi GPIO 0 0 700 640, wiring diagram 0 0 1200 500
- Max 20KB per file, no scripts/foreignObject/embedded raster
- Accessibility: role="img", aria-labelledby, <title>, <desc>

### venv
- .venv exists from Phase 1: Python 3.14.3
- Activate: source .venv/bin/activate
- All dev deps installed; pytest runs 62 tests on macOS with mocked pigpio

### Board Status
- All 6 continuity tests PASSED on the physical CX-2600A board
- Cut traces did NOT affect any switch-to-RIOT paths

## [2026-03-24] Task 5: Single-pin toggle implementation
Implemented single-pin toggle support in GPIOMonitor by detecting toggle configs with pin+positions (excluding power), routing edge callbacks through positions low/high mapping, and reading startup state from the same mapping in read_all_states(). Preserved dual-pin toggle and momentary behavior by keeping legacy low-only toggle callback path when positions are absent, plus explicit backward-compat tests. Verified config.py required no change because validation only checks integer values for keys containing "pin", so positions dict is ignored as intended.

## [2026-03-24] Task 6: Config migration to single-pin toggle schema
Migrated `config/switches.example.yaml` from dual-pin format (pin_color/pin_bw, pin_a/pin_b, pin_2/pin_3) to single-pin with positions schema. Updated 4 toggle switches:
- `tv_type`: pin_color:4 + pin_bw:17 → pin:4 with positions {low:"bw", high:"color"}
- `difficulty_left`: pin_a:23 + pin_b:24 → pin:23 with positions {low:"b", high:"a"}
- `difficulty_right`: pin_a:25 + pin_b:5 → pin:25 with positions {low:"b", high:"a"}
- `channel`: pin_2:6 + pin_3:13 → pin:6 with positions {low:"3", high:"2"}

Updated `config.py.pin_assignments` property to generate backward-compat position keys (e.g., tv_type_color→4, tv_type_bw→4 both map to pin 4). Updated test to expect single-pin behavior (all position values map to same BCM pin). All 66 tests pass, YAML validates, Config.from_file() succeeds, no dual-pin keys remaining in config file.

## [2026-03-24] Task 4: Hardware guide rewrite
Rewrote `docs/hardware-guide.md` to ~350+ lines (34 table rows) incorporating comprehensive IC socket wiring instructions. Moved safety warnings to top with a prominent 5V overvoltage callout. Added sections for Understanding the Atari Board (RIOT pinout), 5V mitigation (desoldering resistors), IC socket mapping table, and troubleshooting. Integrated 3 SVG diagrams and the existing Atari schematic. Preserved and updated BOM, LED, fan, and port cutout sections to align with single-pin toggle config. All 8 QA checks passed, verifying pin consistency, section order, and reference integrity.

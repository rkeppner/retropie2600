# Remove 5V Overvoltage Mitigation Section

## TL;DR

> **Quick Summary**: Remove the entire 5V overvoltage mitigation section and all related warnings from the hardware guide and SVG diagrams, because no power is applied to the Atari motherboard — the 24KΩ pull-up resistors are inert.
> 
> **Deliverables**:
> - Cleaned `docs/hardware-guide.md` — Section 4 removed, sections renumbered, stale references fixed
> - Cleaned `docs/diagrams/atari-to-pi-wiring.svg` — pull-up resistor note and Pin 20 warning removed
> - Cleaned `docs/diagrams/6532-riot-socket.svg` — Pin 20 warning styling and "DO NOT CONNECT" legend removed
> 
> **Estimated Effort**: Quick
> **Parallel Execution**: YES — 2 tasks in Wave 1
> **Critical Path**: Tasks 1+2 (parallel) → F1 (verification)

---

## Context

### Original Request
The hardware guide contains a full section on 5V overvoltage mitigation (removing 24KΩ pull-up resistors from the Atari board). However, no power is or will be applied to the Atari motherboard — the only power source is the Raspberry Pi's DC adapter. Without power on the Atari board's 5V rail, the pull-up resistors are inert and cannot generate dangerous voltage. The entire overvoltage section is therefore unnecessary and misleading.

### Interview Summary
**Key Decisions**:
- Remove Section 4 ("5V Overvoltage Mitigation — MUST DO BEFORE WIRING") entirely — no replacement
- Remove Pin 20 VCC warnings from hardware guide (user confirmed: remove, not reword)
- Remove the critical 5V safety warning from Section 1
- Clean up SVG diagrams: remove pull-up resistor removal note, Pin 20 ⚠ styling, "DO NOT CONNECT" legend
- Troubleshooting: reword "Pin reads LOW" entry (keep floating pin diagnostic, remove 5V mitigation reference), remove "5V detected" entry entirely
- Renumber all subsequent sections (5→4, 6→5, ..., 15→14)

### Metis Review
**Identified Gaps** (addressed):
- SVG diagrams contain overvoltage/VCC references — included in scope
- Pin 20 warnings serve dual purpose (voltage + soldering proximity) — user decided: remove entirely
- Troubleshooting line 255 has valid diagnostic info — user decided: reword, don't remove
- Legitimate 5V references (BOM, fan, Pi pinout) must be preserved — guardrail set

---

## Work Objectives

### Core Objective
Remove all 5V overvoltage mitigation content from the hardware guide and SVG diagrams since no power is applied to the Atari motherboard.

### Concrete Deliverables
- `docs/hardware-guide.md` — Section 4 removed, sections renumbered 1-14, stale references cleaned
- `docs/diagrams/atari-to-pi-wiring.svg` — Pull-up resistor note removed, Pin 20 warning removed
- `docs/diagrams/6532-riot-socket.svg` — Pin 20 label simplified, "DO NOT CONNECT" legend removed

### Definition of Done
- [ ] `docs/hardware-guide.md` has 14 sections numbered sequentially
- [ ] Zero mentions of "overvoltage", "5V mitigation", "MUST DO BEFORE WIRING", or "Section 4"
- [ ] Legitimate 5V references preserved (BOM, fan, Pi pinout)
- [ ] SVGs are valid XML after edits
- [ ] All tests still pass

### Must Have
- Complete removal of Section 4 content (lines 58-78)
- Removal of critical 5V warning from Section 1 (lines 7-8)
- Removal of both Pin 20 VCC warnings (lines 101, 164)
- Sequential section renumbering (1 through 14, no gaps)
- Reworded troubleshooting entry for "Pin reads LOW" (remove 5V mitigation reference, keep pull-up diagnostic)
- Removal of "5V detected on GPIO pin" troubleshooting entry
- SVG cleanup: pull-up resistor note, Pin 20 ⚠ styling, "DO NOT CONNECT" legend

### Must NOT Have (Guardrails)
- Do NOT remove legitimate 5V references: "5V Micro-USB Power Supply" (BOM), "5V Fan" (BOM), "Pin 4 (5V)" (fan), "5V Power" (Pi GPIO SVG labels)
- Do NOT add replacement content explaining why overvoltage isn't a concern — user said remove, not replace
- Do NOT modify Section 3 (Understanding the Atari 2600 Board)
- Do NOT rewrite surrounding paragraphs for "flow" — surgical removals only
- Do NOT change the "Power Off Before Wiring" safety warning (line 16) — that's about Pi power, not Atari voltage
- Do NOT change line 141 (Pi internal pull-ups reference) — legitimate
- Do NOT modify `rpi-gpio-header.svg` — its "5V Power" labels are Pi pinout references, not Atari voltage warnings
- Do NOT touch any Python code, YAML config, test files, or non-docs files
- Do NOT modify SVG visual layout/coordinates beyond text content changes

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES (66 pytest tests)
- **Automated tests**: Not applicable — docs-only change, but run existing tests to verify no breakage
- **Framework**: pytest

### QA Policy
Every task includes agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Markdown**: Bash (grep/python) — verify section numbering, removed references, preserved references
- **SVG**: Bash (python XML parsing) — validate well-formed XML after edits

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — both edits in parallel):
├── Task 1: Edit docs/hardware-guide.md — remove overvoltage content + renumber [quick]
└── Task 2: Edit SVG diagrams — remove overvoltage/VCC warnings [quick]

Wave FINAL (After Wave 1):
└── Task F1: Verification — grep checks + XML validation [quick]
-> Present results -> Get explicit user okay
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | F1 | 1 |
| 2 | — | F1 | 1 |
| F1 | 1, 2 | — | FINAL |

### Agent Dispatch Summary

- **Wave 1**: **2 tasks** — T1 → `quick`, T2 → `quick`
- **FINAL**: **1 task** — F1 → `quick`

---

## TODOs

- [ ] 1. Edit `docs/hardware-guide.md` — Remove overvoltage content and renumber sections

  **What to do**:

  **Step A — Remove critical 5V warning from Section 1 (lines 7-8):**
  Remove these two lines:
  ```
  ⚠️ **CRITICAL: Voltage protection required before connecting to Pi GPIO pins.**
  The original Atari board has 24KΩ pull-up resistors that pull switch lines to +5V when open. 5V exceeds the Pi's 3.3V GPIO maximum input voltage. This will damage the Pi instantly. You MUST complete the 5V Overvoltage Mitigation section before connecting any wires to the Raspberry Pi.
  ```

  **Step B — Remove entire Section 4 (lines 58-78):**
  Remove from `## 4. ⚠️ 5V Overvoltage Mitigation — MUST DO BEFORE WIRING` through the end of the section (line 78: `4. **If you see 5V, STOP.** Do not connect the Pi.`), including the blank line after it.

  **Step C — Remove Pin 20 VCC warning from IC Socket Pin Reference (line 101):**
  Remove this line entirely:
  ```
  ⚠️ **WARNING:** Pin 20 (VCC, +5V) is located at the bottom-left of the socket. Pin 21 (B/W-COLOR) is at the bottom-right. Be extremely careful when soldering near Pin 21 to avoid an accidental bridge to Pin 20.
  ```

  **Step D — Remove Pin 20 VCC caution from Step-by-Step wiring (line 164):**
  Remove this line entirely:
  ```
  - ⚠️ **CAUTION:** Pin 20 is VCC (+5V) and is located at the bottom-left. Pin 21 is at the bottom-right. Do NOT connect or bridge to Pin 20.
  ```

  **Step E — Reword troubleshooting entry (line 255):**
  Change from:
  ```
  - **"Pin reads LOW all the time":** This indicates a floating pin. Verify that the 5V mitigation (resistor removal) was successful and that the Pi's internal pull-up is enabled in the software.
  ```
  To:
  ```
  - **"Pin reads LOW all the time":** This indicates a floating pin. Verify that the Pi's internal pull-up is enabled in the software configuration.
  ```

  **Step F — Remove "5V detected" troubleshooting entry (line 257):**
  Remove this line entirely:
  ```
  - **"5V detected on GPIO pin":** **STOP IMMEDIATELY.** Do not power on the Pi. This means the 5V pull-up resistors have not been removed or bypassed. Re-read Section 4.
  ```

  **Step G — Renumber all sections after removed Section 4:**
  - `## 5. IC Socket Pin Reference` → `## 4. IC Socket Pin Reference`
  - `## 6. GPIO Pin Assignment Table` → `## 5. GPIO Pin Assignment Table`
  - `## 7. IC Socket Wiring Approach` → `## 6. IC Socket Wiring Approach`
  - `## 8. Step-by-Step Wiring Instructions` → `## 7. Step-by-Step Wiring Instructions`
  - `## 9. Power LED Installation` → `## 8. Power LED Installation`
  - `## 10. Fan Installation` → `## 9. Fan Installation`
  - `## 11. Port Cutout Guide` → `## 10. Port Cutout Guide`
  - `## 12. /boot/config.txt Configuration` → `## 11. /boot/config.txt Configuration`
  - `## 13. Testing Your Wiring` → `## 12. Testing Your Wiring`
  - `## 14. Troubleshooting` → `## 13. Troubleshooting`
  - `## 15. References` → `## 14. References`

  **Must NOT do**:
  - Do NOT remove: line 16 ("Power Off Before Wiring"), line 29 ("5V Micro-USB"), line 30 ("5V Fan"), line 141 (Pi internal pull-ups), line 198 ("Pin 4 (5V)")
  - Do NOT add replacement text for the removed section
  - Do NOT rewrite surrounding paragraphs
  - Do NOT modify Section 3 content

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Straightforward text removals and find-replace renumbering in a single markdown file
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: F1
  - **Blocked By**: None

  **References** (CRITICAL):

  **Pattern References**:
  - `docs/hardware-guide.md:7-8` — Critical 5V warning to remove
  - `docs/hardware-guide.md:58-78` — Entire Section 4 to remove
  - `docs/hardware-guide.md:101` — Pin 20 VCC warning to remove
  - `docs/hardware-guide.md:164` — Pin 20 VCC caution to remove
  - `docs/hardware-guide.md:255` — Troubleshooting entry to reword (keep diagnostic, remove 5V reference)
  - `docs/hardware-guide.md:257` — Troubleshooting entry to remove entirely

  **WHY Each Reference Matters**:
  - Line numbers are exact — use them to locate content precisely
  - Lines 7-8 and 58-78 are the primary removals
  - Lines 101 and 164 are secondary Pin 20 warnings confirmed for removal
  - Line 255 must be REWORDED (not removed) — the floating pin diagnostic is still valid
  - Line 257 must be REMOVED — it references the deleted Section 4

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Section count is correct (14 sections)
    Tool: Bash
    Steps:
      1. Run: python3 -c "c=open('docs/hardware-guide.md').read(); import re; sections=re.findall(r'^## \d+\.', c, re.MULTILINE); print(f'{len(sections)} sections: {sections}'); assert len(sections)==14, f'Expected 14, got {len(sections)}'"
    Expected Result: 14 sections, numbered 1-14 sequentially
    Evidence: .sisyphus/evidence/task-1-section-count.txt

  Scenario: No stale overvoltage references
    Tool: Bash
    Steps:
      1. Run: python3 -c "c=open('docs/hardware-guide.md').read().lower(); terms=['overvoltage','5v mitigation','must do before wiring','section 4','re-read section','pull-up resistors have not been removed']; found=[t for t in terms if t in c]; print(f'Found: {found}'); assert not found, f'Stale references: {found}'"
    Expected Result: Zero stale references found
    Evidence: .sisyphus/evidence/task-1-no-stale-refs.txt

  Scenario: Legitimate 5V references preserved
    Tool: Bash
    Steps:
      1. Run: python3 -c "c=open('docs/hardware-guide.md').read(); checks=['5V Micro-USB','5V Fan','Pin 4 (5V)','Power Off Before Wiring','internal pull-up']; found=[t for t in checks if t in c]; print(f'Preserved: {len(found)}/{len(checks)} — {found}'); assert len(found)==len(checks), f'Missing: {set(checks)-set(found)}'"
    Expected Result: All 5 legitimate references preserved
    Evidence: .sisyphus/evidence/task-1-preserved-refs.txt

  Scenario: No Pin 20 VCC warnings remain
    Tool: Bash
    Steps:
      1. Run: python3 -c "c=open('docs/hardware-guide.md').read(); assert 'Pin 20' not in c, 'Pin 20 reference still present'; assert 'VCC' not in c, 'VCC reference still present'; print('PASS: No Pin 20/VCC warnings')"
    Expected Result: Zero matches for "Pin 20" or "VCC"
    Evidence: .sisyphus/evidence/task-1-no-pin20.txt

  Scenario: Troubleshooting entry reworded correctly
    Tool: Bash
    Steps:
      1. Run: python3 -c "c=open('docs/hardware-guide.md').read(); assert 'floating pin' in c, 'Floating pin diagnostic missing'; assert '5V mitigation' not in c, '5V mitigation still referenced'; assert 'internal pull-up is enabled in the software configuration' in c, 'Reworded text missing'; print('PASS: Troubleshooting reworded correctly')"
    Expected Result: Floating pin diagnostic present, 5V mitigation absent, new wording present
    Evidence: .sisyphus/evidence/task-1-troubleshooting.txt
  ```

  **Evidence to Capture:**
  - [ ] task-1-section-count.txt
  - [ ] task-1-no-stale-refs.txt
  - [ ] task-1-preserved-refs.txt
  - [ ] task-1-no-pin20.txt
  - [ ] task-1-troubleshooting.txt

  **Commit**: YES (groups with Task 2)
  - Message: `docs: remove 5V overvoltage section — Atari board has no power source`
  - Files: `docs/hardware-guide.md`, `docs/diagrams/atari-to-pi-wiring.svg`, `docs/diagrams/6532-riot-socket.svg`

- [ ] 2. Edit SVG diagrams — Remove overvoltage/VCC warning content

  **What to do**:

  **Step A — Edit `docs/diagrams/atari-to-pi-wiring.svg`:**

  1. Line 137 — Change the note text. Current content:
     ```
     ⚠ NOTE: POWER (BCM 26) and CHANNEL (BCM 6) switches wire directly to switch contacts. Remove 24KΩ pull-up resistors.
     ```
     Change to:
     ```
     NOTE: POWER (BCM 26) and CHANNEL (BCM 6) switches wire directly to switch contacts, not through the RIOT socket.
     ```
     (Remove ⚠ symbol and the pull-up resistor sentence. Keep the note about POWER/CHANNEL direct wiring — that's still useful.)

  2. Line 168 — Remove the Pin 20 VCC warning entirely:
     ```xml
     <text x="680" y="12" font-family="Arial" font-size="12" fill="#718096" font-style="italic">Warning: RIOT Pin 20 (VCC) is adjacent to Pin 21</text>
     ```
     Remove this entire `<text>` element.

  **Step B — Edit `docs/diagrams/6532-riot-socket.svg`:**

  1. Lines 120-122 — Simplify Pin 20 visual styling. Change the line, circle, and text from red warning to muted gray (matching other unused pins like Pin 19):
     ```xml
     <!-- BEFORE -->
     <line x1="160" y1="580" x2="140" y2="580" stroke="#E53E3E" stroke-width="4" />
     <circle cx="135" cy="580" r="5" fill="#E53E3E" />
     <text x="125" y="584" text-anchor="end" font-weight="bold" fill="#E53E3E">20: VCC (+5V) ⚠</text>
     
     <!-- AFTER -->
     <line x1="160" y1="580" x2="140" y2="580" stroke="#CCCCCC" stroke-width="4" />
     <circle cx="135" cy="580" r="5" fill="#CCCCCC" />
     <text x="125" y="584" text-anchor="end" fill="#555555">20: VCC</text>
     ```
     (Change red `#E53E3E` to muted gray `#CCCCCC`/`#555555` matching unused pins like Pin 19. Remove bold, remove `(+5V) ⚠`. Keep "20: VCC" label for accuracy.)

  2. Lines 237-239 — Remove the VCC legend entry entirely:
     ```xml
     <!-- VCC Legend -->
     <rect x="228" y="0" width="12" height="12" rx="2" fill="#E53E3E"/>
     <text x="248" y="10" fill="#000000">VCC (Pin 20) - DO NOT CONNECT</text>
     ```
     Remove all three lines (comment + rect + text).

  **Must NOT do**:
  - Do NOT modify `rpi-gpio-header.svg` — its "5V Power" labels are Pi pinout references
  - Do NOT change SVG viewBox, dimensions, or coordinate layout
  - Do NOT change any pin labels other than Pin 20
  - Do NOT add new elements or text

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Small targeted text edits in two SVG files — find and replace/remove specific lines
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: F1
  - **Blocked By**: None

  **References** (CRITICAL):

  **Pattern References**:
  - `docs/diagrams/atari-to-pi-wiring.svg:137` — Note text with pull-up resistor removal instruction
  - `docs/diagrams/atari-to-pi-wiring.svg:168` — Pin 20 VCC warning text element
  - `docs/diagrams/6532-riot-socket.svg:119-122` — Pin 20 label with red/bold/⚠ warning styling
  - `docs/diagrams/6532-riot-socket.svg:237-239` — VCC legend entry (comment + rect + text)

  **WHY Each Reference Matters**:
  - Line 137: Contains "Remove 24KΩ pull-up resistors" which directly contradicts the premise of this change
  - Line 168: Pin 20 VCC warning — user confirmed removal
  - Lines 119-122: Pin 20 in red with ⚠ implies danger that doesn't exist
  - Lines 237-239: "DO NOT CONNECT" legend entry reinforces the false danger narrative

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Both SVGs are still valid XML after edits
    Tool: Bash
    Steps:
      1. Run: python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/diagrams/atari-to-pi-wiring.svg'); ET.parse('docs/diagrams/6532-riot-socket.svg'); print('Both SVGs valid XML')"
    Expected Result: Exit code 0, "Both SVGs valid XML"
    Evidence: .sisyphus/evidence/task-2-svg-valid.txt

  Scenario: Pull-up resistor removal note is gone from wiring SVG
    Tool: Bash
    Steps:
      1. Run: python3 -c "c=open('docs/diagrams/atari-to-pi-wiring.svg').read(); assert 'pull-up' not in c.lower(), 'pull-up reference found'; assert 'Remove 24K' not in c, 'Remove 24K found'; print('PASS: No pull-up references')"
    Expected Result: Zero matches for pull-up or "Remove 24K"
    Evidence: .sisyphus/evidence/task-2-no-pullup.txt

  Scenario: Pin 20 warning removed from wiring SVG
    Tool: Bash
    Steps:
      1. Run: python3 -c "c=open('docs/diagrams/atari-to-pi-wiring.svg').read(); assert 'Pin 20 (VCC)' not in c, 'Pin 20 VCC warning still present'; print('PASS: No Pin 20 VCC warning')"
    Expected Result: Zero matches
    Evidence: .sisyphus/evidence/task-2-wiring-no-pin20.txt

  Scenario: Pin 20 fully de-warned in RIOT socket SVG
    Tool: Bash
    Steps:
      1. Run: python3 -c "c=open('docs/diagrams/6532-riot-socket.svg').read(); assert 'DO NOT CONNECT' not in c, 'DO NOT CONNECT legend still present'; assert '(+5V) ⚠' not in c, 'Warning text still present'; assert '#E53E3E' not in c, 'Red warning color still present on line/circle/text'; assert '20: VCC' in c, 'Pin 20 label removed entirely (should still show VCC)'; print('PASS: Pin 20 de-warned — label kept, warning styling removed')"
    Expected Result: No red color (#E53E3E), no "DO NOT CONNECT", no "(+5V) ⚠", but "20: VCC" label preserved in muted gray
    Evidence: .sisyphus/evidence/task-2-riot-pin20.txt

  Scenario: POWER/CHANNEL note preserved (just reworded)
    Tool: Bash
    Steps:
      1. Run: python3 -c "c=open('docs/diagrams/atari-to-pi-wiring.svg').read(); assert 'POWER' in c and 'CHANNEL' in c, 'POWER/CHANNEL note removed'; assert 'wire directly' in c.lower() or 'directly to' in c.lower(), 'Direct wiring note removed'; print('PASS: POWER/CHANNEL note preserved')"
    Expected Result: POWER/CHANNEL direct wiring note still present
    Evidence: .sisyphus/evidence/task-2-note-preserved.txt
  ```

  **Evidence to Capture:**
  - [ ] task-2-svg-valid.txt
  - [ ] task-2-no-pullup.txt
  - [ ] task-2-wiring-no-pin20.txt
  - [ ] task-2-riot-pin20.txt
  - [ ] task-2-note-preserved.txt

  **Commit**: YES (groups with Task 1)
  - Message: `docs: remove 5V overvoltage section — Atari board has no power source`
  - Files: `docs/diagrams/atari-to-pi-wiring.svg`, `docs/diagrams/6532-riot-socket.svg`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 1 verification agent runs after both edits. Must APPROVE. Present results to user and get explicit "okay."

- [ ] F1. **Combined Verification** — `quick`
  Run ALL QA scenarios from Tasks 1 and 2. Additionally:
  - Run `source .venv/bin/activate && python -m pytest tests/ -q --no-header` to confirm no test breakage.
  - Run `python3 -c "import xml.etree.ElementTree as ET; [ET.parse(f'docs/diagrams/{f}') for f in ['6532-riot-socket.svg', 'rpi-gpio-header.svg', 'atari-to-pi-wiring.svg']]; print('All 3 SVGs valid')"` to verify all SVGs (including untouched `rpi-gpio-header.svg`).
  - Verify `rpi-gpio-header.svg` was NOT modified: `git diff docs/diagrams/rpi-gpio-header.svg` should show no changes.
  Output: `Sections [14/14] | Stale Refs [0] | SVGs Valid [3/3] | Tests [PASS] | VERDICT: APPROVE/REJECT`

---

## Commit Strategy

- **Commit 1** (after Wave 1, Tasks 1+2): `docs: remove 5V overvoltage section — Atari board has no power source`
  - Files: `docs/hardware-guide.md`, `docs/diagrams/atari-to-pi-wiring.svg`, `docs/diagrams/6532-riot-socket.svg`
  - Pre-commit: `python3 -c "import xml.etree.ElementTree as ET; [ET.parse(f'docs/diagrams/{f}') for f in ['6532-riot-socket.svg','atari-to-pi-wiring.svg']]; print('SVGs valid')" && python3 -c "import re; c=open('docs/hardware-guide.md').read(); sections=re.findall(r'^## \d+\.', c, re.MULTILINE); assert len(sections)==14; print('14 sections OK')"`

---

## Success Criteria

### Verification Commands
```bash
# Section count = 14
python3 -c "import re; c=open('docs/hardware-guide.md').read(); s=re.findall(r'^## \d+\.', c, re.MULTILINE); print(f'{len(s)} sections'); assert len(s)==14"

# No stale overvoltage references
python3 -c "c=open('docs/hardware-guide.md').read().lower(); assert 'overvoltage' not in c; assert '5v mitigation' not in c; assert 'must do before wiring' not in c; print('Clean')"

# Legitimate 5V refs preserved
python3 -c "c=open('docs/hardware-guide.md').read(); assert '5V Micro-USB' in c; assert '5V Fan' in c; assert 'Pin 4 (5V)' in c; print('Preserved')"

# SVGs valid
python3 -c "import xml.etree.ElementTree as ET; [ET.parse(f'docs/diagrams/{f}') for f in ['6532-riot-socket.svg','rpi-gpio-header.svg','atari-to-pi-wiring.svg']]; print('All valid')"

# Tests pass
source .venv/bin/activate && python -m pytest tests/ -q --no-header
```

### Final Checklist
- [ ] Section 4 (overvoltage) completely removed
- [ ] Sections numbered 1-14 sequentially
- [ ] No Pin 20 VCC warnings in hardware guide
- [ ] Troubleshooting "Pin reads LOW" entry reworded
- [ ] "5V detected" troubleshooting entry removed
- [ ] SVG pull-up resistor note removed
- [ ] SVG Pin 20 warning styling simplified
- [ ] SVG "DO NOT CONNECT" legend removed
- [ ] All 3 SVGs valid XML
- [ ] Legitimate 5V references intact
- [ ] All 66 tests pass

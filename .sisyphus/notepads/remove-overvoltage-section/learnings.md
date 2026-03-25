# Learnings — remove-overvoltage-section

## 2026-03-25 Session: ses_2ee535174ffeGWmw5BosvOReyo

### Context
- No power is applied to the Atari motherboard — only the Raspberry Pi DC adapter powers the system
- The Atari board's 24KΩ pull-up resistors are inert without a power source
- This makes the entire 5V overvoltage section unnecessary and misleading

### Key Decisions (user-confirmed)
- Remove Section 4 ("5V Overvoltage Mitigation") entirely — no replacement text
- Remove Pin 20 VCC warnings from hardware guide (lines 101, 164) — no reword
- Reword troubleshooting "Pin reads LOW" entry — keep floating pin diagnostic, drop 5V reference
- Remove "5V detected on GPIO pin" troubleshooting entry entirely
- Clean up SVGs: remove pull-up resistor note, Pin 20 red/⚠ styling, "DO NOT CONNECT" legend
- Renumber sections from 15 → 14 (remove section 4, everything after shifts down by 1)

### Legitimate 5V References to PRESERVE
These must NOT be removed:
- "5V Micro-USB Power Supply" (BOM, line 29)
- "5V Fan" (BOM, line 30)
- "Pin 4 (5V)" (fan installation, line 198)
- "5V Power" labels in rpi-gpio-header.svg (Pi pinout, not Atari voltage)
- "internal pull-up" (Pi pull-ups reference, line 141)
- "Power Off Before Wiring" (Pi power safety, line 16)

### File Line Map (pre-edit)
- hardware-guide.md:7-8 — Critical 5V warning to remove
- hardware-guide.md:58-78 — Entire Section 4 to remove
- hardware-guide.md:101 — Pin 20 VCC warning to remove
- hardware-guide.md:164 — Pin 20 VCC caution to remove
- hardware-guide.md:255 — Reword (keep floating pin, drop 5V mitigation)
- hardware-guide.md:257 — Remove "5V detected" troubleshooting entry
- atari-to-pi-wiring.svg:137 — Remove "Remove 24KΩ pull-up resistors", keep POWER/CHANNEL note
- atari-to-pi-wiring.svg:168 — Remove Pin 20 VCC warning text element
- 6532-riot-socket.svg:120-122 — Change red styling (#E53E3E) to muted gray (#CCCCCC/#555555), simplify label to "20: VCC"
- 6532-riot-socket.svg:237-239 — Remove VCC legend entry (comment + rect + text)

### SVG NOT to Touch
- rpi-gpio-header.svg — its "5V Power" labels are Pi pinout references

## SVG Editing Task 2: Overvoltage Warning Removal

**Successful patterns:**
- Read both files first to identify exact text/elements before editing
- Use Edit tool with surgical replacements on exact XML matches
- SVG text entities like &#9888; (⚠) and &#937; (Ω) render in SVG as HTML entities
- Pin styling in 6532-riot-socket.svg uses three linked elements (line + circle + text) that must all be updated together
- Legend entries are complete blocks (comment + shape + text) that can be removed entirely
- Gray colors for unused pins are #CCCCCC (line/circle stroke) and #555555 (text fill)

**Verification approach:**
- XML parsing validates structure integrity
- Python string searches confirm removal of warning keywords
- Preserve functional content (e.g., POWER/CHANNEL info) while removing danger messaging
- All 5 QA checks passed on first attempt


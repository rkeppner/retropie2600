# Issues — hardware-guide-upgrade

## [2026-03-25] Session ses_2ee535174ffeGWmw5BosvOReyo

### Resolved Issues

#### Pin Source Conflict (RESOLVED)
- FSM (FD100133) said B/W-COLOR = Pin 21 ✅ CORRECT
- Earlier librarian erroneously said Pin 28 (confused data bus D5 with PB3) — WRONG
- Wikipedia SVG from Rockwell R6532 datasheet CONFIRMS: Pin 21 = PB3 (B/W-COLOR) ✅
- Physical board continuity test CONFIRMS all 5 RIOT pins ✅
- DO NOT second-guess these pin numbers again

#### Momus Plan Review (RESOLVED — 2 rounds)
Round 1 rejections fixed:
- F2/F4 scope checks now allow code+config+docs (not docs-only)
- Task 2 pin labels: 8 active pins only, freed pins unlabeled
- Task 3 QA: checks only 5 single-pin BCM connections
- Duplicate commit block in Task 4 removed

Round 2 rejections fixed:
- AC-4 grep -oP replaced with Python one-liner (macOS BSD grep has no -P flag)
- .venv prerequisite documented in QA Policy
- Verification Strategy updated to mention pytest for code changes

### Known Gotchas
- macOS BSD grep does NOT support -P (PCRE). Use python3 -c "..." for regex extraction instead.
- Inline SVG is stripped by GitHub. Always use external .svg files via ![alt](path.svg).
- Pin 20 (VCC) is adjacent to Pin 21 (PB3/B/W-COLOR) on opposite sides of the DIP socket. Warn users.

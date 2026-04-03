# Decisions — hardware-guide-upgrade

## [2026-03-25] Session ses_2ee535174ffeGWmw5BosvOReyo

### User Decisions (FINAL — do not revisit)
1. **Wiring approach**: IC socket only + config change — all 5 console switches via RIOT socket, ONE wire per switch, single-pin toggle detection
2. **Config update**: YES — update switches.example.yaml to single-pin format as part of this plan
3. **SVG format**: External .svg files in docs/diagrams/ — NOT inline SVG in markdown
4. **docs/diagrams/ directory**: Create it as part of Task 1

### Architectural Decisions
- Single-pin toggles use `positions:` key with `low:` and `high:` sub-keys
- Dual-pin toggle backward compatibility MUST be preserved
- daemon.py is NOT modified — generic event routing already works
- config.py: `positions:` key must NOT be validated as a BCM pin number
- Task ordering: Wave 1 (T1,T2,T3,T5 parallel) → Wave 2 (T6, then T4) → Final Wave (F1-F4 parallel)

### Commit Strategy
1. `feat(gpio): add single-pin toggle detection for IC socket wiring` — gpio_monitor.py + tests
2. `docs: add SVG wiring diagrams for Atari-to-Pi connections` — docs/diagrams/*.svg
3. `config: update switches.example.yaml to single-pin toggle config` — config/switches.example.yaml
4. `docs: rewrite hardware guide with IC socket wiring instructions` — docs/hardware-guide.md

# Project 2 Debug Log

---

## Entry 1 — 2026-02-23 | Project 2 Creation

**Status:** Initial setup complete
**Branch:** `project-2` (merged into `main`)

### What was built
- `dialog_engine.py` — Parses the DSL script file, performs rule matching, returns `(speak_text, [action_tags])`. Tracks scope level and variables.
- `action_runner.py` — Maps action tags (`<head_yes>`, `<head_no>`, `<arm_raise>`, `<dance90>`) to robot primitives. Runs actions from a background thread queue.
- `app.py` — Extended from Project 1 with a `/dialog` POST endpoint accepting `{"text": "user input"}`.
- Supporting files carried over from Project 1: `robot.py`, `motor.py`, `servo.py`, `head.py`, `speaker.py`, `maestro.py`, `templates/`

### Notes
- Project 2 branch was created off `main` and subsequently merged back into `main`.
- No hardware issues encountered during initial push (dev machine, no Maestro connected).

---

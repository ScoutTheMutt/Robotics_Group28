# Debug Log - Robotics Project

## Summary
This debug log documents the evolution of our robot control system, tracking both hardware and software issues encountered during development. A key discovery was our incorrect assumption about servo center positions, which led to mechanical alignment problems.

**Total Entries:** 6
**Hardware Issues:** 4
**Software Issues:** 2
**Incorrect Assumptions Discovered:** 1

---

## Entry 1 - 2026-02-09: Templates Folder Restructure
**Type:** SOFTWARE
**File(s):** `index.html`
**Commit:** 691c63a
**Issue:** Web application structure needed proper organization
**Fix:** Moved `index.html` to `templates/` folder for better Flask app structure
**Impact:** Web server can now properly serve templates using Flask conventions

---

## Entry 2 - 2026-02-09: Servo Speed Defaults Reduced
**Type:** HARDWARE
**File(s):** `Project_1/robot.py:46,58`
**Commit:** a6a8db3
**Issue:** Robot moving too fast with default speeds, causing instability
**Fix:**
- Reduced `driveForward()` default speed from 0.5 to 0.25
- Reduced `driveBackward()` default speed from 0.5 to 0.25
- Reduced `turnLeft()` default speed from 0.3 to 0.15
- Reduced `turnRight()` default speed from 0.3 to 0.15
**Impact:** More controlled and stable robot movement at default speeds

---

## Entry 3 - 2026-02-09: Motor Speed Limits Capped
**Type:** HARDWARE
**File(s):** `Project_1/robot.py:53,65,77,89`
**Commit:** a6a8db3
**Issue:** Maximum speed of 1.0 was too fast for safe operation
**Fix:** Changed speed limit from `min(1.0, speed)` to `min(0.75, speed)` across all drive functions
**Impact:** Robot now caps at 75% speed, preventing dangerous high-speed movements

---

## Entry 4 - 2026-02-09: Joystick Y-Axis Inversion Bug Fixed
**Type:** SOFTWARE
**File(s):** `Project_1/index.html:262`
**Commit:** 9351327
**Issue:** Joystick up/down direction was inverted - pushing up caused robot to go backward
**Fix:** Removed negation from `normalizedY` calculation: changed from `-y / maxRadius` to `y / maxRadius`
**Comment Added:** "FIXED: Flip Y axis so up is forward, down is backward"
**Impact:** Joystick controls now match intuitive expectations (up = forward, down = backward)

---

## Entry 5 - 2026-02-09: Waist Servo Center Position Corrected ⚠️ INCORRECT ASSUMPTION
**Type:** HARDWARE
**File(s):** `Project_1/robot.py:28-30`
**Commit:** 9351327
**Issue:** Waist servo default center position (0°) was mechanically incorrect
**Incorrect Assumption:** We initially assumed the servo's center position corresponded to 0° in our coordinate system, which is typical for many servo implementations. However, testing revealed the actual mechanical neutral position of our waist servo assembly is at -35°. This was likely due to how the servo horn was mounted on the physical assembly.
**Fix:**
- Set waist servo center to -35° instead of 0°
- Calculated position: `waist_center = 6000 - int((35.0 / 90.0) * 2000)`
- Updated Servo initialization to use `default_position=waist_center`
**Note:** Added comment "Center position is -35 degrees (not 0)"
**Impact:** Robot waist now centers at correct mechanical neutral position
**Lesson Learned:** Always physically verify servo zero positions after assembly, as mounting orientation affects the relationship between software angles and physical positions

---

## Entry 6 - 2026-02-09: Waist Rotation Range Limited
**Type:** HARDWARE
**File(s):** `Project_1/index.html:214`
**Commit:** 9351327
**Issue:** Full 90° rotation range exceeded mechanical limits
**Fix:** Changed waist rotation max from 90° to 20° in web interface slider
**Range:** Updated from `min="-90" max="90"` to `min="-90" max="20"`
**Default Value:** Changed from 0° to -35° to match center position
**Impact:** Prevents servo damage from exceeding mechanical rotation limits

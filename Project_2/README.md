# Project 2 — Dialog Engine Test Guide

## Setup & Running

1. Copy project to robot:
```bash
scp -r "/path/to/Project_2" group28@ip:~/
```

2. SSH into robot:
```bash
ssh group28@ip
```

3. Run the server:
```bash
cd ~/Project_2
python app.py --script Documents/testDialogFileForPractice.txt
```

4. Open browser and navigate to `http://ip:5000`

---

## Test Inputs

### Greetings (triggers `<arm_raise>`)
| Type this | Expected response |
|---|---|
| `hello` | Random greeting + arm raise |
| `hi` | Random greeting + arm raise |
| `hey robot` | Random greeting + arm raise |

### Variable Capture & Recall
| Type this | Expected response |
|---|---|
| `my name is Ryan` | "Nice to meet you, Ryan" + head nod |
| `what is my name` | "Your name is Ryan" |
| `i am 20 years old` | "Got it. You are 20 years old" + head nod |
| `how old am i` | "You are 20 years old" |
| `what is my favorite color` | "I don't know" (variable never set) |

### Actions
| Type this | Action triggered |
|---|---|
| `dance` | `<dance90>` — robot dances |
| `dance for me` | `<dance90>` — robot dances |
| `raise your arm` | `<arm_raise>` — arm raises |
| `wave at me` | `<arm_raise>` — arm raises |
| `yes` | `<head_yes>` — head nods |
| `no` | `<head_no>` — head shakes |

### Nested Scope Test (u → u1 → u2)
| Step | Type this | Expected response |
|---|---|---|
| 1 | `let us talk` | "Sure. Ask me a question." |
| 2 | `are you happy` | Yes response + head nod |
| 2 | `are you sad` | No response + head shake |
| 3 (after sad) | `why` | "Because I am a robot." + arm raise |

### Miscellaneous
| Type this | Expected response |
|---|---|
| `tell me something cool` | Random fun fact + head nod |
| `thank you` | "You are welcome." + head nod |
| `bye` | "Goodbye!" + arm raise |
| `say hello` | Picks a random greeting + arm raise |
| `robot` | "I heard you." + head nod |
| `you are awesome` | "Thanks!" + head nod + arm raise |
| `do the secret move` | "Absolutely." — logs warning about unknown `<moonwalk>` tag |

### Safety Interrupt
| Type this | Expected behavior |
|---|---|
| `stop` | Cancels all actions, stops wheels, resets to IDLE |
| `cancel` | Same as stop |
| `reset` | Same as stop |
| `quit` | Same as stop |

---

## What to Watch

- Keep an eye on the **robot terminal output** — it prints state transitions, rule matches, and action start/end (required for demo).
- After 4 consecutive unmatched inputs in a nested scope, the engine resets to IDLE.
- `<moonwalk>` is an unknown tag — a warning should appear in the terminal but the robot won't crash.

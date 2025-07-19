# 🎮 Xbox Controller Drift Fixer (Contoler.py)

This Python project solves **joystick drift** issues by creating a **virtual Xbox 360 controller** and redirecting real controller inputs with smart corrections. It's especially useful when your physical controller has hardware stick drift — notably on Axis 1 (Y-axis), where values like `0.51562` cause unwanted in-game movement.

---

## ⚙️ Features

- ✅ Real-time **drift correction** with aggressive tuning for heavy drift
- 🧠 Smart detection of **user intent** (so corrections don’t fight real input)
- 🎯 Calibrated for **Axis 1 major drift**
- 🎮 Virtual controller emulation using `vgamepad`
- 🔁 Live input remapping from real to virtual controller (buttons, triggers, sticks, D-Pad)
- 🧼 Graceful cleanup on exit
- 🪄 Auto-start with pre-known drift profile

---

## 📸 Demo

> Coming Soon (GIF or video showing the script fixing drift in a game)

---

## 📦 Requirements

- Python 3.8+
- Windows (required for vgamepad and admin permissions)
- Xbox 360 or compatible controller

### 🔧 Python Dependencies

Install them with pip:

```bash
pip install pygame vgamepad

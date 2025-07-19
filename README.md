# 🎮 Xbox Controller Drift Fixer (Contoler.py)

Fix stick drift from your real Xbox controller by redirecting inputs to a virtual controller with real-time correction. This tool is perfect for users experiencing **unwanted joystick movement** due to hardware issues — especially with **Axis 1 (Y-axis)** stuck around `0.51`.

---

## 📸 Visual Demo – Real vs Virtual Controller Drift

### 🎮 Real Controller (With Drift)
<img src="https://raw.githubusercontent.com/CodeStartUp/controler-drift-fix/main/images/Screenshot%202025-07-19%20103441.png" width="500"/>

> Stick Y-axis (AXIS 1) is stuck at **0.51562** – this causes constant movement in games even when idle.

---

### 🕹️ Virtual Controller (After Correction)
<img src="https://raw.githubusercontent.com/CodeStartUp/controler-drift-fix/main/images/Screenshot%202025-07-19%20103452.png" width="500"/>

> Drift removed! Axis value becomes **0.00**, restoring control to the player.

---

## ⚙️ Features

- 🧠 Real-time **drift correction** (especially for AXIS 1)
- 🛠️ Pre-configured correction for known drift values
- 🧼 Applies **deadzone** and **adaptive calibration**
- 🎯 Ignores drift but **respects real input**
- 🕹️ Emulates Xbox 360 controller with `vgamepad`
- 🔁 Redirects all inputs: buttons, sticks, triggers, and D-Pad

---

## 📦 Requirements

- ✅ Windows 10/11
- ✅ Python 3.8+
- ✅ Admin privileges to run
- ✅ A physical Xbox 360 / Xbox One controller

### 🧪 Python Dependencies

Install with:

```bash
pip install pygame vgamepad

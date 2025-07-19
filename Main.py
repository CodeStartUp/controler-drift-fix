# Contoler.py
import pygame
import time
import sys
import math
from collections import deque
from vgamepad import VX360Gamepad, XUSB_BUTTON

class XboxDriftFix:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        # Configuration for aggressive drift correction
        self.DRIFT_SAMPLES = 300  # More samples for better calibration
        self.BASE_DEADZONE = 0.05  # Smaller deadzone since we're handling drift
        self.DRIFT_THRESHOLD = 0.01  # Correct even small drifts
        self.MAX_AXIS_VALUE = 32767
        self.POLL_RATE = 120
        self.DRIFT_ADAPT_RATE = 0.01  # Faster adaptation to new drift
        
        # Your specific drift values (from diagnostic)
                #           AXIAS 0, AXIS 1, AXIS 2, AXIS 3                
        self.KNOWN_DRIFT = [0.00002, 0.51562, 0.00002, -0.00002]
        
        # State variables
        self.stick_drift = self.KNOWN_DRIFT.copy()
        self.active_deadzones = [self.BASE_DEADZONE] * 4
        self.calibration_data = deque(maxlen=self.DRIFT_SAMPLES)
        self.calibrated = True  # Start with your known values
        self.last_values = [0.0] * 4
        self.input_history = [[] for _ in range(4)]

        # Button mapping
        self.BUTTON_MAP = {
            0: XUSB_BUTTON.XUSB_GAMEPAD_A,
            1: XUSB_BUTTON.XUSB_GAMEPAD_B,
            2: XUSB_BUTTON.XUSB_GAMEPAD_X,
            3: XUSB_BUTTON.XUSB_GAMEPAD_Y,
            4: XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            5: XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            6: XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            7: XUSB_BUTTON.XUSB_GAMEPAD_START,
            8: XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            9: XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB
        }

        # D-pad mapping (hat 0)
        self.DPAD_MAP = {
            (0, 1): XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            (0, -1): XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            (-1, 0): XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            (1, 0): XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
            (1, 1): XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP | XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
            (-1, 1): XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP | XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            (1, -1): XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN | XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
            (-1, -1): XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN | XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT
        }

        self.real_ctrl = None
        self.virtual_ctrl = None
        self.init_controllers()
        
        print("⚠️ Using pre-configured drift values:")
        print(f"AXIS 0: {self.stick_drift[0]:.5f}")
        print(f"AXIS 1: {self.stick_drift[1]:.5f} (MAJOR DRIFT)")
        print(f"AXIS 2: {self.stick_drift[2]:.5f}")
        print(f"AXIS 3: {self.stick_drift[3]:.5f}")

    def init_controllers(self):
        if pygame.joystick.get_count() == 0:
            print("❌ No controller found.")
            sys.exit(1)

        self.real_ctrl = pygame.joystick.Joystick(0)
        self.real_ctrl.init()
        self.virtual_ctrl = VX360Gamepad()

        print(f"✅ Controller connected: {self.real_ctrl.get_name()}")

    def detect_user_input(self, axis_idx, current_value):
       
        self.input_history[axis_idx].append(current_value)
        if len(self.input_history[axis_idx]) > 10:
            self.input_history[axis_idx].pop(0)
        
        # If we see rapid changes, it's likely user input
        if len(self.input_history[axis_idx]) > 2:
            changes = [abs(self.input_history[axis_idx][i] - self.input_history[axis_idx][i-1]) 
                      for i in range(1, len(self.input_history[axis_idx]))]
            avg_change = sum(changes) / len(changes)
            return avg_change > 0.1  # Threshold for intentional movement
        
        return False

    def correct_axis(self, axis_idx, raw_value):
        # Special handling for AXIS 1 with major drift
        if axis_idx == 1:
            # Apply aggressive correction for your 0.51562 drift
            corrected = raw_value - self.stick_drift[axis_idx]
            
            # If user is pushing against the drift, let them through
            if raw_value > 0.55 and raw_value > self.stick_drift[axis_idx]:
                corrected = raw_value  # Bypass correction
            elif raw_value < -0.1:  # Only correct positive drift for AXIS 1
                corrected = raw_value  # Bypass correction
            
            # Apply deadzone only if we're not in user input mode
            if abs(corrected) < self.active_deadzones[axis_idx] and not self.detect_user_input(axis_idx, raw_value):
                corrected = 0.0
        else:
            # Normal correction for other axes
            corrected = raw_value - self.stick_drift[axis_idx]
            if abs(corrected) < self.active_deadzones[axis_idx]:
                corrected = 0.0

        # Keep values in valid range
        return max(min(corrected, 1.0), -1.0)

    def process_inputs(self):
        pygame.event.pump()
        
        # Process axes with drift correction
        num_axes = min(6, self.real_ctrl.get_numaxes())  # Now checking up to 6 axes for triggers
        raw_axes = [self.real_ctrl.get_axis(i) for i in range(num_axes)]
        
        # Apply corrections to sticks
        left_x = self.correct_axis(0, raw_axes[0]) if num_axes > 0 else 0.0
        left_y = -self.correct_axis(1, raw_axes[1]) if num_axes > 1 else 0.0  # Inverted Y
        right_x = self.correct_axis(2, raw_axes[2]) if num_axes > 2 else 0.0
        right_y = -self.correct_axis(3, raw_axes[3]) if num_axes > 3 else 0.0

        # Process triggers (axes 4 and 5 typically)
        left_trigger = (raw_axes[4] + 1) / 2 if num_axes > 4 else 0.0  # Convert from (-1 to 1) to (0 to 1)
        right_trigger = (raw_axes[5] + 1) / 2 if num_axes > 5 else 0.0

        # Process D-pad (hat 0)
        dpad_state = (0, 0)
        if self.real_ctrl.get_numhats() > 0:
            dpad_state = self.real_ctrl.get_hat(0)

        # Update virtual controller
        self.virtual_ctrl.left_joystick(
            x_value=int(left_x * self.MAX_AXIS_VALUE),
            y_value=int(left_y * self.MAX_AXIS_VALUE)
        )
        self.virtual_ctrl.right_joystick(
            x_value=int(right_x * self.MAX_AXIS_VALUE),
            y_value=int(right_y * self.MAX_AXIS_VALUE)
        )
        
        # Set trigger values (0 to 255)
        self.virtual_ctrl.left_trigger(value=int(left_trigger * 255))
        self.virtual_ctrl.right_trigger(value=int(right_trigger * 255))

        # Process buttons
        for i in range(min(self.real_ctrl.get_numbuttons(), len(self.BUTTON_MAP))):
            btn_state = self.real_ctrl.get_button(i)
            btn = self.BUTTON_MAP[i]
            if btn_state:
                self.virtual_ctrl.press_button(btn)
            else:
                self.virtual_ctrl.release_button(btn)

        # Process D-pad
        if dpad_state != (0, 0):
            dpad_buttons = self.DPAD_MAP.get(dpad_state, 0)
            if dpad_buttons:
                if dpad_buttons & XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP:
                    self.virtual_ctrl.press_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                else:
                    self.virtual_ctrl.release_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                
                if dpad_buttons & XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN:
                    self.virtual_ctrl.press_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                else:
                    self.virtual_ctrl.release_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                
                if dpad_buttons & XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT:
                    self.virtual_ctrl.press_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                else:
                    self.virtual_ctrl.release_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                
                if dpad_buttons & XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT:
                    self.virtual_ctrl.press_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                else:
                    self.virtual_ctrl.release_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        else:
            # Release all D-pad buttons if not pressed
            self.virtual_ctrl.release_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            self.virtual_ctrl.release_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            self.virtual_ctrl.release_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            self.virtual_ctrl.release_button(XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)

        self.virtual_ctrl.update()

    def cleanup(self):
        if self.virtual_ctrl:
            self.virtual_ctrl.reset()
            if hasattr(self.virtual_ctrl, 'close'):
                self.virtual_ctrl.close()
        pygame.quit()
        print("🧹 Clean exit.")

    def run(self):
        try:
            while True:
                start_time = time.time()
                self.process_inputs()
                elapsed = time.time() - start_time
                sleep_time = max(0, (1 / self.POLL_RATE) - elapsed)
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
        except Exception as e:
            print(f"\n⚠️ Error: {e}")
        finally:
            self.cleanup()


if __name__ == "__main__":
    if sys.platform == "win32":
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("⚠️ Please run as Administrator.")
            sys.exit(1)

    controller = XboxDriftFix()
    controller.run()


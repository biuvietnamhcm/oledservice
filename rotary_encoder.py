"""
Rotary encoder handler using gpiozero (event-driven, no polling)
"""

from gpiozero import RotaryEncoder, Button
from gpiozero.pins.rpigpio import RPiGPIOFactory


class RotaryEncoderHandler:
    """
    Handles rotary encoder input with gpiozero (event-based)

    GPIO Pins (BCM numbering):
    - GPIO 6  -> Push button (SW)
    - GPIO 25 -> A / CLK
    - GPIO 27 -> B / DT
    """

    def __init__(self, pin_push=25, pin_a=26, pin_b=16):
        try:
            factory = RPiGPIOFactory()

            self.rotation_callbacks = []
            self.button_callbacks = []

            # Create rotary encoder
            self.encoder = RotaryEncoder(
                a=pin_a,
                b=pin_b,
                max_steps=0,        # unlimited rotation
                wrap=False,
                pin_factory=factory
            )

            # Create push button
            self.button = Button(
                pin=pin_push,
                pull_up=True,
                pin_factory=factory,
                bounce_time=0.05    # hardware debounce
            )

            # Attach event handlers
            self.encoder.when_rotated = self._handle_rotation
            self.button.when_pressed = self._handle_button

            print(f"[Rotary] Initialized (Push={pin_push}, A={pin_a}, B={pin_b})")

        except Exception as e:
            print(f"[Rotary] Initialization error: {e}")
            self.encoder = None
            self.button = None

    # ==============================
    # Internal Event Handlers
    # ==============================

    def _handle_rotation(self):
        """
        Called automatically by gpiozero when rotated
        """
        delta = self.encoder.steps

        # Determine direction
        direction = 1 if delta > 0 else -1

        # Reset steps so next event is clean
        self.encoder.steps = 0

        for callback in self.rotation_callbacks:
            try:
                callback(direction, 1)
            except Exception as e:
                print(f"[Rotary] Rotation callback error: {e}")

    def _handle_button(self):
        """
        Called automatically when button pressed
        """
        for callback in self.button_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"[Rotary] Button callback error: {e}")

    # ==============================
    # Public API
    # ==============================

    def on_rotation(self, callback):
        """
        Register rotation callback:
        callback(direction, steps)
        direction: 1 (CW) or -1 (CCW)
        """
        self.rotation_callbacks.append(callback)

    def on_button_press(self, callback):
        """
        Register button press callback:
        callback()
        """
        self.button_callbacks.append(callback)

    def cleanup(self):
        """
        Clean up GPIO resources
        """
        try:
            if self.encoder:
                self.encoder.close()
            if self.button:
                self.button.close()
            print("[Rotary] Cleaned up")
        except Exception as e:
            print(f"[Rotary] Cleanup error: {e}")


# ==============================
# Standalone Test
# ==============================

if __name__ == "__main__":

    rotary = RotaryEncoderHandler()

    def on_rotate(direction, steps):
        print(f"Rotated: {'Clockwise' if direction > 0 else 'Counter-clockwise'}")

    def on_button():
        print("Button pressed!")

    rotary.on_rotation(on_rotate)
    rotary.on_button_press(on_button)

    print("Rotate or press the encoder... (Ctrl+C to exit)")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        rotary.cleanup()
        print("Done.")
# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

from machine import Pin
from machine import bitstream
import utime
import math

LED_CHANNEL1 = 21
LED_CHANNEL2 = 20

sin_table = [int(512 * (1 + math.sin(2 * math.pi * i / 256 - math.pi/2)))
             for i in range(256)]

del math


class NeoPixel:
    # NeoPixel driver for MicroPython
    # MIT license; Copyright (c) 2016 Damien P. George, 2021 Jim Mussared
    # G R B W
    ORDER = (1, 0, 2, 3)

    def __init__(self, pin, n, bpp=3, timing=1):
        self.pin = pin
        self.n = n
        self.bpp = bpp
        self.buf = bytearray(n * bpp)
        self.pin.init(pin.OUT)
        # or a user-specified timing ns tuple (high_0, low_0, high_1, low_1).
        self.timing = (
            ((400, 850, 800, 450) if timing else (400, 1000, 1000, 400))
            if isinstance(timing, int)
            else timing
        )

    def __len__(self):
        return self.n

    def __setitem__(self, i, v):
        offset = i * self.bpp
        for i in range(self.bpp):
            self.buf[offset + self.ORDER[i]] = v[i]

    def __getitem__(self, i):
        offset = i * self.bpp
        return tuple(self.buf[offset + self.ORDER[i]] for i in range(self.bpp))

    def fill(self, v):
        b = self.buf
        l = len(self.buf)
        bpp = self.bpp
        for i in range(bpp):
            c = v[i]
            j = self.ORDER[i]
            while j < l:
                b[j] = c
                j += bpp

    def write(self):
        # BITSTREAM_TYPE_HIGH_LOW = 0
        bitstream(self.pin, 0, self.timing, self.buf)


class LEDController:
    """
    A singleton class to control an LED.
    """

    _instances = {}

    def __new__(cls, led_channel, *args, **kwargs):
        if led_channel not in cls._instances:
            cls._instances[led_channel] = super(LEDController, cls).__new__(cls)
        return cls._instances[led_channel]

    def __init__(self, led_channel):
        """
        Initializes the LEDController instance for controlling an LED based \
            on the specified channel.
        This method sets up the LED effects, initializes the current effect \
            index, repeat count, duration, and start time.
        It then maps the provided LED channel to its corresponding pin number \
            and initializes the NeoPixel object.

        Args:
            led_channel (str): The channel number of the LED, either "LED1" \
                or "LED2".
        Raises:
            ValueError: If the provided led_channel is not "LED1" or "LED2".
        Example:
            >>> led_controller = LEDController("LED1")
            >>> # The LEDController instance is now initialized with LED1's \
pin configuration.
        Note:
            The led_channel parameter should be a string matching either \
                "LED1" or "LED2".
            The actual pin numbers for "LED1" and "LED2" are defined in the \
                led_pins_map dictionary.
            The NeoPixel object is initialized with the pin number and the \
                number of LEDs (4 in this case).
        See Also:
            NeoPixel: The class used to control the NeoPixel LED strip.
        """
        # Ensure __init__ only initializes once
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        # Map LED1 and LED2 to their respective pin numbers
        self.led_pins_map = {"LED1": LED_CHANNEL1, "LED2": LED_CHANNEL2}

        if led_channel not in self.led_pins_map:
            raise ValueError("Invalid LED channel")

        self.effects = [
            self._solid_effect, self._blink_effect, self._breathing_effect
        ]
        self.sin_table = sin_table
        self.channel = led_channel
        self.current_effect_index = 0
        self.repeat_count = 0
        self.duration = 0
        self.current_effect_start_time = 0
        self.duty_cycle = 0
        self.led_index = 0
        self.rgb = 0x000000
        self.is_on = False

        pin = Pin(self.led_pins_map[led_channel], Pin.OUT)
        self.np = NeoPixel(pin, 4, timing=0)

        for i in range(4):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def reinit(self):
        self.current_effect_index = 0
        self.repeat_count = 0
        self.duration = 0
        self.current_effect_start_time = 0

        pin = Pin(self.led_pins_map[self.channel], Pin.OUT)
        self.np = NeoPixel(pin, 4, timing=0)

    def _breathing_effect(self):
        current_time = utime.ticks_ms()
        elapsed_time = utime.ticks_diff(current_time,
                                        self.current_effect_start_time)
        index = (elapsed_time % self.duration) * 256 // self.duration
        self.duty_cycle = self.sin_table[index]

        for i in range(4):
            if self.led_index & (1 << i):
                r = (self.duty_cycle * ((self.rgb >> 16) & 0xFF)) // 1024
                g = (self.duty_cycle * ((self.rgb >> 8) & 0xFF)) // 1024
                b = (self.duty_cycle * (self.rgb & 0xFF)) // 1024
                self.np[i] = (r, g, b)
            else:
                self.np[i] = (0, 0, 0)
        self.np.write()

    def _blink_effect(self):
        current_time = utime.ticks_ms()
        elapsed_time = utime.ticks_diff(current_time,
                                        self.current_effect_start_time)
        if elapsed_time < self.duration / 2:
            if self.is_on is False:
                self.is_on = True
                for i in range(4):
                    if self.led_index & (1 << i):
                        self.np[i] = ((self.rgb >> 16) & 0xFF,
                                      (self.rgb >> 8) & 0xFF, self.rgb & 0xFF)
                    else:
                        self.np[i] = (0, 0, 0)
                self.np.write()
        else:
            if self.is_on is True:
                self.is_on = False
                for i in range(4):
                    self.np[i] = (0, 0, 0)
                self.np.write()

    def _solid_effect(self):
        if self.is_on is False:
            self.is_on = True
            for i in range(4):
                if self.led_index & (1 << i):
                    self.np[i] = ((self.rgb >> 16) & 0xFF,
                                  (self.rgb >> 8) & 0xFF, self.rgb & 0xFF)
                else:
                    self.np[i] = (0, 0, 0)
                pass
            self.np.write()

    def timing_proc(self):
        """
        Callback function to update the LED effect.
        This method is called at regular intervals to update the current \
            LED effect.

        Args:
            None
        Returns:
            None
        """
        current_effect = self.effects[self.current_effect_index]
        current_effect()
        self._update_effect()

    def _update_effect(self):
        current_time = utime.ticks_ms()
        elapsed_time = utime.ticks_diff(current_time,
                                        self.current_effect_start_time)
        if elapsed_time >= self.duration:
            if self.repeat_count != 0xFF:
                self.repeat_count -= 1
            if self.repeat_count > 0:
                self.current_effect_start_time = current_time

    def set_led_effect(self, mod, duration, repeat_count, led_index, rgb):
        """
        Sets the LED effect.
        This method configures the LED with the specified effect, duration, 
        repeat count, LED index, and RGB color.

        Args:
            mod (int): The index of the effect to set.
                - mod = 0: solid effect
                - mod = 1: blink effect
                - mod = 2: breathing effect
            duration (int): The duration of the effect in milliseconds.
            repeat_count (int): The number of times to repeat the effect.
                Must be between 0 and 255.
                A value of 255( 0xFF ) represents infinite repetition.
            led_index (int): The index of the LED to control.
                Each bit represents the index of an LED 
                (e.g., the first bit represents OUT1, the second 
                bit represents OUT2).
            rgb (int): The RGB color value of the LED in hexadecimal.

        Returns:
            None

        Raises:
            ValueError: If mod, repeat_count, or led_index is out of range,
                or if rgb is not a valid hexadecimal color code.

        Example:
            >>> # Solid red on LED1 for 1 second
            >>> set_led_effect(0, 1000, 5, 0b0001, 0xFF0000)
            >>> # Blink green on LED1 and LED2 indefinitely
            >>> set_led_effect(1, 500, 255, 0b0011, 0x00FF00)
        """
        if not 0 <= mod < len(self.effects):
            print("[LEDS]Invalid effect index. Must be between 0 and 2.")
            return

        if not isinstance(repeat_count,
                          int) or repeat_count < 0 or repeat_count > 255:
            print("[LEDS]Invalid repeat count.")
            return
        self.current_effect_index = mod
        self.duration = duration
        self.repeat_count = repeat_count
        self.duty_cycle = 0
        self.led_index = led_index
        self.rgb = rgb
        self.is_on = False
        self.current_effect_start_time = utime.ticks_ms()


if __name__ == '__main__':
    import uasyncio

    async def _main():
        COLOR_WHITE = 0xFFFFFF
        COLOR_LIGHT_BLUE = 0x40CFFF
        COLOR_LIGHT_RED = 0xFF4040

        led_1 = LEDController("LED1")
        led_2 = LEDController("LED2")

        async def period_task():
            while True:
                led_1.timing_proc()
                led_2.timing_proc()
                await uasyncio.sleep(0.01)

        async def ctrl_task():
            while True:
                led_1.set_led_effect(2, 800, 0xFF, 0x0F, COLOR_WHITE)
                led_2.set_led_effect(2, 800, 0xFF, 0x0F, COLOR_WHITE)
                await uasyncio.sleep(1.6)

                led_1.set_led_effect(1, 800, 0xFF, 0x0F, COLOR_LIGHT_BLUE)
                led_2.set_led_effect(1, 800, 0xFF, 0x0F, COLOR_LIGHT_BLUE)
                await uasyncio.sleep(1.6)

                led_1.set_led_effect(0, 0, 0xFF, 0x0F, COLOR_LIGHT_RED)
                led_2.set_led_effect(0, 0, 0xFF, 0x0F, COLOR_LIGHT_RED)
                await uasyncio.sleep(1.6)

        await uasyncio.gather(period_task(), ctrl_task())

    uasyncio.run(_main())

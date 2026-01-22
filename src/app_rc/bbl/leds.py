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
from app_rc.i18n import t

LED_CHANNEL1 = 21
LED_CHANNEL2 = 20

# Precompute a sine table for breathing effect (0–255 brightness)
sin_table = [int(255 * (1 + math.sin(2 * math.pi * i / 256 - math.pi / 2)) / 2) for i in range(256)]
del math


class NeoPixel:
    """
    NeoPixel driver for MicroPython.
    MIT license; Copyright (c) 2016 Damien P. George,
    2021 Jim Mussared.
    Color order: GRBW
    """
    ORDER = (1, 0, 2, 3)

    def __init__(self, pin, n, bpp=3, timing=1):
        self.pin = pin
        self.n = n
        self.bpp = bpp
        self.buf = bytearray(n * bpp)
        self.pin.init(pin.OUT)
        self.timing = (
            ((400, 850, 800, 450) if timing else (400, 1000, 1000, 400))
            if isinstance(timing, int)
            else timing
        )

    def __len__(self):
        return self.n

    def __setitem__(self, i, v):
        offset = i * self.bpp
        for j in range(self.bpp):
            self.buf[offset + self.ORDER[j]] = v[j]

    def __getitem__(self, i):
        offset = i * self.bpp
        return tuple(self.buf[offset + self.ORDER[j]] for j in range(self.bpp))

    def fill(self, v):
        b = self.buf
        l = len(b)
        bpp = self.bpp
        for i in range(bpp):
            c = v[i]
            j = self.ORDER[i]
            while j < l:
                b[j] = c
                j += bpp

    def write(self):
        bitstream(self.pin, 0, self.timing, self.buf)


class LEDController:
    """
    A singleton class to control NeoPixel LEDs with multiple effects.
    """

    _instances = {}

    def __new__(cls, led_channel, *args, **kwargs):
        if led_channel not in cls._instances:
            cls._instances[led_channel] = super(LEDController, cls).__new__(cls)
        return cls._instances[led_channel]

    def __init__(self, led_channel):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.led_pins_map = {
            "LED1": LED_CHANNEL1,
            "LED2": LED_CHANNEL2
        }

        if led_channel not in self.led_pins_map:
            raise ValueError(t("led_invalid_channel"))

        self.effects = [
            self._solid_effect,
            self._blink_effect,
            self._breathing_effect
        ]

        self.sin_table = sin_table
        self.channel = led_channel

        self.current_effect_index = None
        self.repeat_count = 0
        self.duration = 0
        self.current_effect_start_time = 0
        self.led_index = 0
        self.rgb = 0x000000
        self.is_on = False

        pin = Pin(self.led_pins_map[led_channel], Pin.OUT)
        self.np = NeoPixel(pin, 4, timing=0)
        self.np.fill((0, 0, 0))
        self.np.write()

    def reinit(self):
        self.__init__(self.channel)

    def _apply_brightness(self, brightness):
        r_base = (self.rgb >> 16) & 0xFF
        g_base = (self.rgb >> 8) & 0xFF
        b_base = self.rgb & 0xFF

        for i in range(4):
            if self.led_index & (1 << i):
                self.np[i] = (
                    (r_base * brightness) // 255,
                    (g_base * brightness) // 255,
                    (b_base * brightness) // 255
                )
            else:
                self.np[i] = (0, 0, 0)
        self.np.write()

    def _breathing_effect(self):
        elapsed = utime.ticks_diff(utime.ticks_ms(), self.current_effect_start_time)
        index = (elapsed % self.duration) * 256 // self.duration
        self._apply_brightness(self.sin_table[index])

    def _blink_effect(self):
        elapsed = utime.ticks_diff(utime.ticks_ms(), self.current_effect_start_time)
        half = self.duration // 2
        new_state = elapsed < half
        if new_state != self.is_on:
            self.is_on = new_state
            self._apply_brightness(255 if self.is_on else 0)

    def _solid_effect(self):
        if not self.is_on:
            self.is_on = True
            self._apply_brightness(255)

    def timing_proc(self):
        if self.current_effect_index is None:
            return
        self.effects[self.current_effect_index]()
        self._update_effect()

    def _update_effect(self):
        current_time = utime.ticks_ms()
        elapsed_time = utime.ticks_diff(current_time, self.current_effect_start_time)

        if elapsed_time >= self.duration:
            if self.repeat_count != 0xFF:
                self.repeat_count -= 1

            if self.repeat_count > 0:
                self.current_effect_start_time = current_time
            else:
                self.current_effect_index = None

    def set_led_effect(self, mod, duration, repeat_count, led_index, rgb):
        if not 0 <= mod < len(self.effects):
            print(t("led_invalid_effect"))
            return

        if not isinstance(repeat_count, int) or not 0 <= repeat_count <= 255:
            print(t("led_invalid_repeat"))
            return

        self.current_effect_index = mod
        self.duration = duration
        self.repeat_count = repeat_count
        self.led_index = led_index
        self.rgb = rgb
        self.is_on = False
        self.current_effect_start_time = utime.ticks_ms()

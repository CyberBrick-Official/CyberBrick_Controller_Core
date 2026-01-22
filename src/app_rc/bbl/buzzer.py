# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

from machine import Pin, PWM
import utime
from app_rc.i18n import t

BUZZER_CHANNEL1 = 21
BUZZER_CHANNEL2 = 20


class BuzzerController:
    """
    A singleton class to control a buzzer (PWM-controlled)
    connected to a specified GPIO pin.

    This class allows setting the frequency, duty cycle,
    and volume of the buzzer.
    It ensures that only one instance of the controller exists per buzzer
    channel (BUZZER1 or BUZZER2).
    """
    _instances = {}

    def __new__(cls, buzzer_channel, freq=10, duty=0):
        if buzzer_channel not in cls._instances:
            cls._instances[buzzer_channel] = super(BuzzerController, cls).__new__(cls)
        return cls._instances[buzzer_channel]

    def __init__(self, buzzer_channel, freq=10, duty=0):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.ch = buzzer_channel
        self.buzzer_pins_map = {
            "BUZZER1": BUZZER_CHANNEL1,
            "BUZZER2": BUZZER_CHANNEL2
        }

        if self.ch not in self.buzzer_pins_map:
            raise ValueError(t("buzzer_invalid_channel"))

        self.buzzer = PWM(Pin(self.buzzer_pins_map[self.ch], Pin.OUT))
        self.set_duty(duty)
        self.set_freq(freq)

    def set_freq(self, freq=10):
        self.buzzer.freq(freq)

    def set_duty(self, duty):
        self.buzzer.duty(duty)

    def set_volume(self, volume=0):
        self.buzzer.duty(int(volume * 512 / 100))

    def stop(self):
        self.buzzer.duty(0)

    def reinit(self, freq=5, duty=0):
        self.buzzer.deinit()
        self.buzzer = PWM(
            Pin(self.buzzer_pins_map[self.ch], Pin.OUT),
            freq=freq,
            duty=duty
        )

    def deinit(self):
        self.buzzer.deinit()


note_frequencies = {
    'C0': 16, 'C#0': 17, 'D0': 18, 'D#0': 19, 'E0': 21, 'F0': 22,
    'F#0': 23, 'G0': 25, 'G#0': 26, 'A0': 28, 'A#0': 29, 'B0': 31,
    'C1': 33, 'C#1': 35, 'D1': 37, 'D#1': 39, 'E1': 41, 'F1': 44,
    'F#1': 46, 'G1': 49, 'G#1': 52, 'A1': 55, 'A#1': 58, 'B1': 62,
    'C2': 65, 'C#2': 69, 'D2': 73, 'D#2': 78, 'E2': 82, 'F2': 87,
    'F#2': 93, 'G2': 98, 'G#2': 104, 'A2': 110, 'A#2': 117, 'B2': 123,
    'C3': 131, 'C#3': 139, 'D3': 147, 'D#3': 156, 'E3': 165, 'F3': 175,
    'F#3': 185, 'G3': 196, 'G#3': 208, 'A3': 220, 'A#3': 233, 'B3': 247,
    'C4': 262, 'C#4': 277, 'D4': 294, 'D#4': 311, 'E4': 330, 'F4': 349,
    'F#4': 370, 'G4': 392, 'G#4': 415, 'A4': 440, 'A#4': 466, 'B4': 494,
    'C5': 523, 'C#5': 554, 'D5': 587, 'D#5': 622, 'E5': 659, 'F5': 698,
    'F#5': 740, 'G5': 784, 'G#5': 831, 'A5': 880, 'A#5': 932, 'B5': 988,
    'C6': 1047, 'C#6': 1109, 'D6': 1175, 'D#6': 1245, 'E6': 1319, 'F6': 1397,
    'F#6': 1480, 'G6': 1568, 'G#6': 1661, 'A6': 1760, 'A#6': 1865, 'B6': 1976,
    'C7': 2093, 'C#7': 2217, 'D7': 2349, 'D#7': 2489, 'E7': 2637, 'F7': 2794,
    'F#7': 2960, 'G7': 3136, 'G#7': 3322, 'A7': 3520, 'A#7': 3729, 'B7': 3951,
    'C8': 4186, 'C#8': 4435, 'D8': 4699, 'D#8': 4978, 'E8': 5274, 'F8': 5588,
    'F#8': 5920, 'G8': 6272, 'G#8': 6645, 'A8': 7040, 'A#8': 7459, 'B8': 7902
}

valid_notes = 'ABCDEFGP'


class MusicController:
    """
    A singleton class to manage and play music through a buzzer
    using RTTTL (Ring Tone Text Transfer Language).
    """
    _instances = {}

    def __new__(cls, buzzer_ch, volume=0):
        if buzzer_ch not in cls._instances:
            cls._instances[buzzer_ch] = super(MusicController, cls).__new__(cls)
        return cls._instances[buzzer_ch]

    def __init__(self, buzzer_ch, volume=0):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.buzzer = BuzzerController(buzzer_ch)
        self.tune = []
        self.volume = volume
        self.tune_index = 0
        self.play_interval = 0
        self.is_playing = False
        self.loop = False

    def set_volume(self, volume=0):
        self.volume = volume

    def stop(self):
        self.is_playing = False
        self.buzzer.set_duty(0)

    def reinit(self):
        self.set_volume(0)
        self.stop()
        self.buzzer.reinit()

    def _rtttl_parse(self, rtttl_str):
        try:
            title, defaults, song = rtttl_str.split(':')
            d, o, b = defaults.split(',')
            d = int(d.split('=')[1])
            o = int(o.split('=')[1])
            b = int(b.split('=')[1])
            whole = (60000 / b) * 4
            note_list = song.split(',')
        except Exception:
            return t("music_invalid_rtttl")

        res_list = []
        for note in note_list:
            for i, ch in enumerate(note):
                if ch.upper() in valid_notes:
                    index = i
                    break
            else:
                continue

            length = note[:index]
            value = note[index:].replace('.', '')

            if not any(c.isdigit() for c in value):
                value += str(o)

            if 'p' in value.lower():
                value = 'p'

            duration = whole / (int(length) if length else d)
            duration = duration * 1.5 if '.' in note else duration

            freq = note_frequencies.get(value.upper(), 0)
            res_list.append([freq, duration])

        return res_list

    def play(self, tune, volume=50, block=True, loop=False):
        self.tune = self._rtttl_parse(tune)
        self.volume = volume

        if type(self.tune) is not list:
            return self.tune

        if not block:
            self.tune_index = 0
            self.is_playing = True
            self.loop = loop
            self.play_interval = utime.ticks_ms()
        else:
            for freq, msec in self.tune:
                freq = max(0, min(freq, 20000))
                msec = max(0, min(msec, 512))

                if freq > 4:
                    self.buzzer.set_freq(freq)
                    self.buzzer.set_duty(int(msec * self.volume / 100))
                else:
                    self.buzzer.stop()

                utime.sleep(msec * 0.001)

            self.buzzer.stop()

    def timing_proc(self):
        if not self.is_playing:
            return

        current_time = utime.ticks_ms()
        if current_time < self.play_interval:
            return

        if self.tune_index >= len(self.tune):
            if self.loop:
                self.tune_index = 0
            else:
                self.stop()
                return

        freq, msec = self.tune[self.tune_index]
        freq = max(0, min(freq, 20000))
        msec = max(0, min(msec, 512))

        if freq > 4:
            self.buzzer.set_freq(freq)
            self.buzzer.set_duty(int(msec * self.volume / 100))
        else:
            self.buzzer.stop()

        self.play_interval = current_time + msec
        self.tune_index += 1

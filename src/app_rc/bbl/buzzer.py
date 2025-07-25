# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

from machine import Pin, PWM
import utime

BUZZER_CHANNEL1 = 21
BUZZER_CHANNEL2 = 20


class BuzzerController:
    """
    A singleton class to control a buzzer (PWM-controlled) \
        connected to a specified GPIO pin.

    This class allows setting the frequency, duty cycle, \
        and volume of the buzzer.
    It ensures that only one instance of the controller exists per buzzer \
        channel (BUZZER1 or BUZZER2).

    Attributes:
        buzzer (PWM): PWM instance for controlling the buzzer.
        ch (str): The buzzer channel, either 'BUZZER1' or 'BUZZER2'.

    Example:
        >>> buzzer = BuzzerController('BUZZER1', freq=1000, duty=512)
        >>> buzzer.set_freq(1500)
        >>> buzzer.set_duty(1023)
        >>> buzzer.set_volume(50)
        >>> buzzer.stop()
    """
    _instances = {}

    def __new__(cls, buzzer_channel, freq=10, duty=0):
        if buzzer_channel not in cls._instances:
            cls._instances[buzzer_channel] = super(BuzzerController, cls).__new__(cls)
        return cls._instances[buzzer_channel]

    def __init__(self, buzzer_channel, freq=10, duty=0):
        """
        Initializes the BuzzerController instance for controlling a buzzer

        Sets the initial frequency and duty cycle for the buzzer

        Args:
            buzzer_channel (str): The buzzer channel,\
                either 'BUZZER1' or 'BUZZER2'.
            freq (int): Frequency for the buzzer (default: 10).
            duty (int): Duty cycle for the buzzer (default: 0).

        Raises:
            ValueError: If the provided buzzer_channel is not valid.

        Example:
            >>> buzzer = BuzzerController('BUZZER1')
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.ch = buzzer_channel
        self.buzzer_pins_map = {
            "BUZZER1": BUZZER_CHANNEL1,
            "BUZZER2": BUZZER_CHANNEL2
        }

        if self.ch not in self.buzzer_pins_map:
            raise ValueError("Invalid BUZZER channel")

        self.buzzer = PWM(Pin(self.buzzer_pins_map[self.ch], Pin.OUT))
        self.set_duty(duty)
        self.set_freq(freq)

    def set_freq(self, freq=10):
        """
        Sets the frequency of the buzzer.

        Args:
            freq (int): The frequency to set for the buzzer.
        Example:
            >>> buzzer.set_freq(1500)  # Sets the buzzer frequency to 1500 Hz
        """
        self.buzzer.freq(freq)

    def set_duty(self, duty):
        """
        Sets the duty cycle for the buzzer.

        Args:
            duty (int): The duty cycle value (0 to 1023).
        Example:
            >>> buzzer.set_duty(512)  # Sets the duty cycle to 50%
        """
        self.buzzer.duty(duty)

    def set_volume(self, volume=0):
        """
        Sets the volume of the buzzer by adjusting the duty cycle.

        The volume is represented as a percentage from 0 to 100, \
            where 0 is silent and 100 is the maximum volume.

        Args:
            volume (int): The volume level, ranging from 0 to 100.
        Example:
            >>> buzzer.set_volume(50)  # Sets the volume to 50%
        """
        self.buzzer.duty(int(volume * 512 / 100))

    def stop(self):
        """
        Stops the buzzer by setting its duty cycle to 0, turning it off.
        Example:
            >>> buzzer.stop()  # Stops the buzzer
        """
        self.buzzer.duty(0)

    def reinit(self, freq=5, duty=0):
        """
        Reinitializes the buzzer by deinitializing and recreating the PWM \
            instance with the specified frequency and duty cycle.

        Args:
            freq (int): \
                The frequency to set after reinitialization (default: 5).
            duty (int): \
                The duty cycle to set after reinitialization (default: 0).
        Example:
            >>> # Reinitializes buzzer with new frequency and duty
            >>> buzzer.reinit(freq=1000, duty=512)
        """
        self.buzzer.deinit()
        self.buzzer = PWM(Pin(self.buzzer_pins_map[self.ch], Pin.OUT),
                          freq=freq, duty=duty)

    def deinit(self):
        """
        Deinitializes the PWM instance controlling the buzzer, \
            effectively turning it off.
        Example:
            >>> buzzer.deinit()  # Deinitializes the buzzer PWM
        """
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
    A singleton class to manage and play music through a buzzer \
        using RTTTL (Ring Tone Text Transfer Language).

    This class parses RTTTL formatted strings and \
        plays the notes on the buzzer with a specified volume.
    The controller ensures that only one instance exists for the \
        given buzzer channel.
    Example:
        >>> music = MusicController('BUZZER1', volume=50)
        >>> music.play('Entertainer:d=4,o=5,b=140:8d,8d#,8e,c6,8e', volume=80)
    """
    _instances = {}

    def __new__(cls, buzzer_ch, volume=0):
        if buzzer_ch not in cls._instances:
            cls._instances[buzzer_ch] = super(MusicController, cls).__new__(cls)
        return cls._instances[buzzer_ch]

    def __init__(self, buzzer_ch, volume=0):
        """
        Initializes the MusicController instance, \
            setting up the buzzer and preparing the necessary attributes.

        Args:
            buzzer_ch (str): \
                The buzzer channel to control (BUZZER1 or BUZZER2).
            volume (int): The initial volume level for the buzzer (0 to 100).
        Example:
            >>> # Initializes the MusicController
            >>> music = MusicController('BUZZER1', volume=50)
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.buzzer = BuzzerController(buzzer_ch)
        self.tune = []
        self.volume = volume
        self.tune_index = 0
        self.play_interval = 0
        self.is_playing = False

    def set_volume(self, volume=0):
        """
        Sets the volume for the music playback \
            by adjusting the buzzer's duty cycle.

        Args:
            volume (int): The volume level, ranging from 0 to 100.
        Example:
            >>> # Sets the volume for music playback to 70%
            >>> music.set_volume(70)
        """
        self.volume = volume

    def stop(self):
        """
        Stops the music playback by setting the buzzer's duty cycle to 0 \
            and halting any ongoing tune.
        Example:
            >>> music.stop()  # Stops the current music playback
        """
        self.is_playing = False
        self.buzzer.set_duty(0)

    def reinit(self):
        """
        Reinitializes the music controller, stopping any music, \
            resetting volume, and reinitializing the buzzer.
        Example:
            >>> music.reinit()  # Reinitializes the music controller
        """
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
            noteList = song.split(',')
        except:
            return 'Invalid RTTTL format.'

        res_list = []
        for note in noteList:
            length = d
            value = ''

            for i in note:
                if i.upper() in valid_notes:
                    index = note.find(i)
                    break
            length = note[0:index]
            value = note[index:].replace('.', '')
            if not any(char.isdigit() for char in value):
                value += str(o)

            if 'p' in value:
                value = 'p'

            length = whole / (int(length) if length else d)
            length = length * 1.5 if '.' in note else length

            freq = note_frequencies.get(value.upper(), 0)

            res_list.append([freq, length])

        return res_list

    def play(self, tune, volume=50, block=True, loop=False):
        """
        Plays a tune by parsing the RTTTL string and \
            sending the corresponding frequencies to the buzzer.

        Args:
            tune (str): \
                The RTTTL formatted string representing the melody to play.
            volume (int): The volume level for playback (0 to 100).
            block (bool): If True, plays the tune synchronously, \
                blocking further code execution.
            loop (bool): If True, \
                the tune will repeat indefinitely after it finishes.
        Example:
            >>> music.play('Entertainer:d=4,o=5,b=140:8d,8d#,8e,c6', volume=80)
        """
        self.tune = self._rtttl_parse(tune)
        self.volume = volume
        if type(self.tune) is not list:
            return self.tune

        if block is False:
            self.tune_index = 0
            self.is_playing = True
            self.loop = loop
            self.play_interval = utime.ticks_ms()
        else:
            for freq, msec in self.tune:
                # print(freq, msec)
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
        """
        A callback method to periodically check and \
            play the next note in the tune.

        This method is called in the event loop and \
            ensures the correct timing for each note based on its duration.
        Example:
            >>> # Call timing_proc in the main loop to play the tune
            >>> music.timing_proc()
        """
        if self.is_playing:
            current_time = utime.ticks_ms()
            if current_time >= self.play_interval:

                if self.tune_index >= len(self.tune):
                    if self.loop:
                        self.tune_index = 0
                    else:
                        self.stop()
                        return

                tone = self.tune[self.tune_index]

                freq = tone[0]
                msec = tone[1]
                # print(freq, msec)

                freq = max(0, min(freq, 20000))
                msec = max(0, min(msec, 512))

                if freq > 4:
                    self.buzzer.set_freq(freq)
                    self.buzzer.set_duty(int(msec * self.volume / 100))
                else:
                    self.buzzer.stop()

                self.play_interval = current_time + msec  # 设置下一个音符的播放时间
                self.tune_index += 1


if __name__ == '__main__':
    import uasyncio

    entertainer = 'Entertainer:d=4,o=5,b=140:8d,8d#,8e,c6,8e,c6,8e,2c6,8c6,8d6,8d#6,8e6,8c6,8d6,e6,8b,d6,2c6,p,8d,8d#,8e,c6,8e,c6,8e,2c6,8p,8a,8g,8f#,8a,8c6,e6,8d6,8c6,8a'

    def _main():
        music = MusicController("BUZZER2")

        async def period_task():
            while True:
                music.timing_proc()
                await uasyncio.sleep(0.005)

        music.play(entertainer, 1, block=False, loop=False)
        # await uasyncio.gather(period_task())

    uasyncio.run(_main())

import utime
import machine

class SleepModule:
    def __init__(self, logger=print):
        self.channels = {}
        self.sleep_callback = None
        self.logger = logger
        self.enabled = True

    def add_channel(self, name, threshold, duration):
        self.channels[name] = {
            'threshold': threshold,
            'duration': duration,
            'last_data': None,
            'start_time': None,
            'stable': False
        }

    def register_data(self, name, data):
        if not self.enabled:
            return

        if name not in self.channels:
            self.logger(f"Channel '{name}' does not exist.")

        ch = self.channels[name]
        if ch['last_data'] is None:
            ch['last_data'] = data
            return

        fluct = abs(data - ch['last_data'])
        ch['last_data'] = data

        if fluct < ch['threshold']:
            if ch['start_time'] is None:
                ch['start_time'] = utime.time()
            else:
                if utime.time() - ch['start_time'] >= ch['duration']:
                    ch['stable'] = True
        else:
            ch['start_time'] = None
            ch['stable'] = False

    def register_sleep_callback(self, callback):
        self.sleep_callback = callback

    def check_all_channels_stable(self):
        if not self.channels:
            return False
        return all(ch['stable'] for ch in self.channels.values())

    def monitor_channels(self):
        if not self.enabled:
            return
        if self.check_all_channels_stable():
            self.logger("[SLEEP] All channels stable, triggering sleep...")
            self.trig_sleep()

    def trig_sleep(self):
        if self.sleep_callback:
            self.logger("[SLEEP] Entering user sleep mode...")
            self.sleep_callback()
        else:
            self.logger("[SLEEP] Entering default sleep mode...")
            machine.deepsleep()

    def disable(self):
        self.enabled = False
        self.channels.clear()
        self.sleep_callback = None

    def enable(self):
        self.enabled = True


if __name__ == '__main__':
    import rc_module
    import utime
    import neopixel
    import machine
    import esp32

    def sleep_handler():
        pin_numbers = [0, 1, 2, 3, 4, 5]
        wake_pins = []
        for num in pin_numbers:
            pin = machine.Pin(num, machine.Pin.IN, machine.Pin.PULL_DOWN)
            if pin.value() == 0:
                wake_pins.append(pin)
            else:
                print(f"[SLEEP] Pin {num} high, skip.")
        if wake_pins:
            esp32.wake_on_ext1(pins=wake_pins, level=esp32.WAKEUP_ANY_HIGH)
        else:
            print("[SLEEP] No wake pins available.")
        np = neopixel.NeoPixel(machine.Pin(8, machine.Pin.OUT), 1)
        np[0] = (0, 0, 0)
        np.write()
        machine.deepsleep()

    ch_names = ['L1', 'L2', 'L3', 'R1', 'R2', 'R3', 'K1', 'K2', 'K3', 'K4']

    rc_module.rc_master_init()
    sleep_module = SleepModule()

    sleep_module.register_sleep_callback(sleep_handler)
    for i in range(6):
        sleep_module.add_channel(ch_names[i], 100, 10)
    for i in range(6, 10):
        sleep_module.add_channel(ch_names[i], 1, 10)

    while True:
        rc_data = rc_module.rc_master_data()

        if rc_data is not None:
            print(rc_data)
            for i, item in enumerate(rc_data):
                sleep_module.register_data(ch_names[i], item)

            sleep_module.monitor_channels()

        utime.sleep(1)

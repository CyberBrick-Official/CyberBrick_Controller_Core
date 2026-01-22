# -*- coding: utf-8 -*-

class I18N:
    def __init__(self, lang="en"):
        self.lang = lang
        self._dict = {
            "en": {
                # motors.py
                "motors.invalid_index": "Invalid motor index.",
                "motors.invalid_index_or_param": "Invalid motor index or parameter.",
                "motors.param_out_of_range_0_100": "Parameter must be between 0 and 100.",
                "motors.param_out_of_range_-100_100": "Parameter must be between -100 and 100.",

                # servos.py
                "servo.invalid_index": "Invalid servo index.",
                "servo.invalid_angle_0_180": "Angle must be between 0 and 180 degrees.",
                "servo.invalid_step_speed": "Step speed must be between 0 and 100.",
                "servo.invalid_speed": "Speed must be between -100 and 100.",

                # leds.py
                "led_invalid_channel": "Invalid LED channel.",
                "led_invalid_effect": "Invalid LED effect mode.",
                "led_invalid_repeat": "Repeat count must be between 0 and 255.",

                # buzzer.py
                "buzzer_invalid_channel": "Invalid buzzer channel.",

                # music (RTTTL)
                "music_invalid_rtttl": "Invalid RTTTL format.",

                # executor.py
                "exec.import_error": "Import error during execution: {err}",
                "exec.execution_error": "Execution error: {err}",
                "exec.timeout": "Command execution timed out.",
                "exec.execution_done": "Execution done.",
                "exec.execution_stopped": "Execution stopped manually.",
                "exec.execution_already_stopped": "Execution already been stopped.",
                "exec.unsafe_command": "Unsafe command detected: {cmd}",
                "exec.run_code_size": "RUN CODE SIZE: {size}"
            },
            "tr": {
                # motors.py
                "motors.invalid_index": "Geçersiz motor numarası.",
                "motors.invalid_index_or_param": "Geçersiz motor numarası veya parametre.",
                "motors.param_out_of_range_0_100": "Parametre 0 ile 100 arasında olmalıdır.",
                "motors.param_out_of_range_-100_100": "Parametre -100 ile 100 arasında olmalıdır.",

                # servos.py
                "servo.invalid_index": "Geçersiz servo numarası.",
                "servo.invalid_angle_0_180": "Açı 0 ile 180 derece arasında olmalıdır.",
                "servo.invalid_step_speed": "Adım hızı 0 ile 100 arasında olmalıdır.",
                "servo.invalid_speed": "Hız -100 ile 100 arasında olmalıdır.",

                # leds.py
                "led_invalid_channel": "Geçersiz LED kanalı.",
                "led_invalid_effect": "Geçersiz LED efekt modu.",
                "led_invalid_repeat": "Tekrar sayısı 0 ile 255 arasında olmalıdır.",

                # buzzer.py
                "buzzer_invalid_channel": "Geçersiz buzzer kanalı.",

                # music (RTTTL)
                "music_invalid_rtttl": "Geçersiz RTTTL müzik formatı.",

                # executor.py
                "exec.import_error": "Çalıştırma sırasında import hatası: {err}",
                "exec.execution_error": "Çalıştırma hatası: {err}",
                "exec.timeout": "Komut çalıştırma zaman aşımına uğradı.",
                "exec.execution_done": "Çalıştırma tamamlandı.",
                "exec.execution_stopped": "Çalıştırma manuel olarak durduruldu.",
                "exec.execution_already_stopped": "Çalıştırma zaten durdurulmuş.",
                "exec.unsafe_command": "Güvensiz komut tespit edildi: {cmd}",
                "exec.run_code_size": "ÇALIŞTIRILAN KOD BOYUTU: {size}"
            }
        }

    def t(self, key):
        return self._dict.get(self.lang, {}).get(key, key)


# fonksiyonel kullanım (leds.py, buzzer.py, executor.py)
_i18n = I18N()

def t(key):
    return _i18n.t(key)

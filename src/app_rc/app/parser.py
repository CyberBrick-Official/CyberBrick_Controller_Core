# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

import ulogger
from devices import Devices
import gc

__all__ = ["DataParser"]

PARSER_NONE = 0
PARSER_RECEIVE1 = 1
PARSER_RECEIVE2 = 2

logger = ulogger.Logger()


class DataParser:
    """
    A class for parsing configuration data.
    """

    def __init__(self):
        """
        Initializes the DataParser instance.

        Attributes:
            data_type (int): The type of data parser.
            config (dict): The configuration data.
            parsed_data (dict): The parsed data.
        """
        self.data_type = PARSER_NONE
        self. id_multiplier = Devices.get_base_multiplier()

    def set_slave_idx(self, data_type):
        """
        Sets the receiver type.

        Args:
            data_type (int): The type of data parser to set.

        Returns:
            None
        """
        self.data_type = data_type

    def parse(self, data):
        """
        Parses the input data based on the set data type. Call only when needed.

        Args:
            data (dict): The data to be parsed.

        Returns:
            dict: The parsed data.
        """
        if not isinstance(data, dict):
            logger.error("[PARSE][CONF] Not dict.")
            return {}
        parsed_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                if key == "sender":
                    parsed_data[key] = self._parse_channels(
                        value["channels"])
                    data[key] = None
                    gc.collect()
                if key == "receiver_1" and self.data_type == PARSER_RECEIVE1:
                    parsed_data[key] = self._parse_dict(value)
                    data[key] = None
                    gc.collect()
                    parsed_data[key] = self._parse_actuator(
                        parsed_data[key])
                if key == "receiver_2" and self.data_type == PARSER_RECEIVE2:
                    parsed_data[key] = self._parse_dict(value)
                    data[key] = None
                    gc.collect()
                    parsed_data[key] = self._parse_actuator(
                        parsed_data[key])

        return parsed_data

    def _parse_dict(self, dictionary):
        """
        Recursively parses a dictionary.

        Args:
            dictionary (dict): The dictionary to be parsed.

        Returns:
            dict: The parsed dictionary.
        """
        parsed_dict = {}
        for key, value in dictionary.items():
            if isinstance(value, dict):
                parsed_dict[key] = self._parse_dict(value)
            elif isinstance(value, list):
                parsed_dict[key] = self._parse_list(value)
            else:
                parsed_dict[key] = value
            dictionary[key] = None
        return parsed_dict

    def _parse_list(self, lst):
        """
        Recursively parses a list with reduced memory usage.
        """
        parsed_list = []
        for i in range(len(lst)):
            item = lst[i]
            if isinstance(item, dict):
                parsed = self._parse_dict(item)
                parsed_list.append(parsed)
            elif isinstance(item, list):
                parsed = self._parse_list(item)
                parsed_list.append(parsed)
            else:
                parsed_list.append(item)
            lst[i] = None
            gc.collect()
        return parsed_list

    def _parse_channels(self, channels):
        """
        Parses the channels data.

        Args:
            channels (list): The channels data to be parsed.

        Returns:
            dict: The parsed channels data.
        """
        parsed_channels = {
            "deadzones": [],
            "mid_values": [],
            "key1": [],
            "key2": [],
            "key3": [],
            "key4": [],
            "p1": [],
            "p2": [],
            "p3": [],
            "p4": [],
            "m1": [],
            "m2": [],
            "adc_ch1": [],
            "adc_ch2": [],
            "adc_ch3": [],
            "adc_ch4": [],
            "adc_ch5": [],
            "adc_ch6": [],
            "buzzer1": [],
            "buzzer2": []
        }
        for i, item in enumerate(channels[:6]):
            adc_ch_str = "adc_ch" + str(i + 1)
            if item:
                data = item.get("data", {})
                parsed_channels["deadzones"].append(data.get("deadzone", 0))
                parsed_channels["mid_values"].append(data.get("mid_value", 0))
                control_data = item.get("controls", [])
                for control in control_data:
                    if control["receiver"] == self.data_type:
                        direction = 1 if control[
                            "direction"] == "positive" else -1
                        if control["actuator"].startswith("MOTOR"):
                            parsed_channels["m" +
                                            control["actuator"][-1]].append(
                                                [i, direction])
                        if control["actuator"].startswith("PWM"):
                            parsed_channels["p" +
                                            control["actuator"][-1]].append(
                                                [i, direction])
                events = item.get("event", [])
                equal_mid_arr = self._match_events(events, "eq_mid")
                above_mid_arr = self._match_events(events, "gt_mid")
                below_mid_arr = self._match_events(events, "lt_mid")
                parsed_equal_mid = self._parse_actuators(equal_mid_arr)
                parsed_above_mid = self._parse_actuators(above_mid_arr)
                parsed_below_mid = self._parse_actuators(below_mid_arr)
                parsed_channels[adc_ch_str] = {
                    "equal_mid": parsed_equal_mid,
                    "above_mid": parsed_above_mid,
                    "below_mid": parsed_below_mid
                }

            else:
                parsed_channels["deadzones"].append(0)
                parsed_channels["mid_values"].append(0)
        index = 0
        for item in channels[6:]:
            index += 1
            key = "key" + str(index)
            if item:
                events = item.get("event", [])
                long_press = self._match_events(events, "long")
                short_press = self._match_events(events, "short")
                press_down = self._match_events(events, "down")
                release = self._match_events(events, "up")
                parsed_long_press = self._parse_actuators(long_press)
                parsed_short_press = self._parse_actuators(short_press)
                parsed_press_down = self._parse_actuators(press_down)
                parsed_release = self._parse_actuators(release)
                parsed_channels[key] = {
                    "short": parsed_short_press,
                    "long": parsed_long_press,
                    "down": parsed_press_down,
                    "release": parsed_release
                }
            else:
                parsed_channels[key] = {
                    "short": [],
                    "long": [],
                    "down": [],
                    "release": []
                }
        return parsed_channels

    def _parse_actuators(self, actuator_data):
        """
        Parses the actuators data.

        Args:
            actuator_data (list): The actuator data to be parsed.

        Returns:
            list: The parsed actuator data.
        """
        ret_list = []
        for item in actuator_data:
            actuator_type = 0
            if "actuator" in item:
                actuator_name = item["actuator"]
                prefix = actuator_name.rstrip("0123456789")  # Extract prefix

                index = 1
                suffix = actuator_name[len(prefix):]
                if suffix.isdigit():
                    index = int(suffix)

                if prefix == "CODE":
                    actuator_type = Devices.CODE_EXEC
                else:
                    base = getattr(Devices, f"{prefix}_1", None)
                    if base is not None:
                        actuator_type = base + index - 1

                if self.data_type == item.get("receiver", 0):
                    data = item.get("set_value", [])

                    ret_list.append(self._get_events_id(actuator_type, data))

        return ret_list

    def _get_events_id(self, actuator, values):
        return [
            (actuator % self.id_multiplier) + (it * self.id_multiplier)
            for it in values
        ]

    def parse_event_id(self, event_id):
        return {
            "actuator": event_id % self.id_multiplier,
            "value": int(event_id / self.id_multiplier)
        }

    def _parse_pwm(self, data):
        pwm_data = []

        if data:
            pwm_data = [
                data.get("initial_value", 0),
                data.get("speed", 0),
                data.get("min_value", 0),
                data.get("max_value", 0),
                data.get("type", "")
            ]
        else:
            pwm_data = [0, 0, 0, 0, ""]
        return pwm_data

    def _parse_motor(self, data, motor_idx):
        motor_data = []
        advanced_config = []
        if data:
            motor_data = [
                data.get("bias", 0),
                data.get("min_value", 0),
                data.get("max_value", 0)
            ]
            adv_cfg = data.get("advance_motor_config", {})
            advanced_config = [
                motor_idx,
                adv_cfg.get("en", False),
                adv_cfg.get("ACC", 0),
                adv_cfg.get("LVZ", 0),
                adv_cfg.get("HVZ", 0),
                adv_cfg.get("HVD", 1)
            ]
        else:
            motor_data = [0, 0, 0]
            advanced_config = [motor_idx, False, 0, 0, 0, 1]

        return motor_data, advanced_config

    def _parse_led(self, data):
        mode = 1 if data.get("mode", "") == "blink" else 0
        rgb_value = int(data.get("RGB", 0x000000), 16)

        led_data = [data["effect"],
                    data["sequence_number"],
                    mode,
                    rgb_value,
                    data.get("repeat_times", 0),
                    data.get("time", 0)
                    ]

        return led_data

    def _parse_buzzer(self, data):
        buzzer_data = [
            data.get("effect", -1),
            data.get("volume", -1),
            data.get("repeat_time", 1),
            data.get("code", "")
        ]
        return buzzer_data

    def _parse_codes(self, data):
        code_data = [
            data.get("effect", -1),
            data.get("code", "")
        ]
        return code_data

    def _parse_actuator(self, data):
        """
        Parses the actuator data.

        Args:
            data (dict): The actuator data to be parsed.

        Returns:
            dict: The parsed actuator data.
        """

        gc.collect()

        extracted_data = {
            "pwm": [],
            "motor": [],
            "led1": [],
            "led2": [],
            "buzzer1": [],
            "buzzer2": [],
            "codes": [],
            "advanced_config": []
        }

        for i in range(1, 5):
            pwm_key = f"PWM{i}"
            if pwm_key in data:
                extracted_data["pwm"].append(self._parse_pwm(data[pwm_key]))

        motor_keys = ("MOTOR1", "MOTOR2")
        for idx, key in enumerate(motor_keys, 1):
            val = data.get(key)
            if val is not None:
                motor_data, adv_conf = self._parse_motor(val, idx)
                extracted_data["motor"].append(motor_data)
                extracted_data["advanced_config"].append(adv_conf)

        led_keys = ("LED1", "LED2")
        for idx, key in enumerate(led_keys, 1):
            led_data = data.get(key)
            if led_data and "data" in led_data:
                parse = self._parse_led
                extracted_data[f"led{idx}"].extend(parse(item) for item in led_data["data"])

        buzzer_keys = ("BUZZER1", "BUZZER2")
        for idx, key in enumerate(buzzer_keys, 1):
            buzzer_data = data.get(key)
            if buzzer_data and "data" in buzzer_data:
                parse = self._parse_buzzer
                extracted_data[f"buzzer{idx}"].extend(parse(item) for item in buzzer_data["data"])

        codes = data.get("CODE")
        if codes and "data" in codes:
            parse = self._parse_codes
            extracted_data["codes"].extend(parse(item) for item in codes["data"])

        gc.collect()  # 解析完再次释放内存
        return extracted_data

    def _match_events(self, events_list, type_str):
        """
        Finds events that match the given type.

        Args:
            events_list (list): The list of events.
            type_str (str): The type of event to match.

        Returns:
            list: The list of matching events.
        """
        ret = []
        for event in events_list:
            type = event.get("type", [])
            if type == type_str:
                ret.append(event)
        return ret

    def parse_simulation_setting(self, actuator_data):
        """
        Parses the simulation setting data.

        Args:
            actuator_data (str): The JSON string containing the actuator data.

        Returns:
            dict: The parsed simulation setting data.
        """
        setting_data = {}
        extracted_data = {
            "pwm": [],
            "motor": [],
            "led1": [],
            "led2": [],
            "buzzer1": [],
            "buzzer2": [],
            "codes": [],
            "advanced_config": []
        }

        if not isinstance(actuator_data, dict):
            logger.error("[PARSE][SIM] Not dict.")
            return {}

        actuator_name = actuator_data.get("actuator", "")
        receiver_idx = actuator_data.get("receiver", 0)

        if actuator_name.startswith("PWM"):
            for pwm_num in range(1, 5):
                pwm_key = f"PWM{pwm_num}"
                if pwm_key == actuator_name:
                    data = actuator_data.get("data", {})
                    extracted_data["pwm"].append(self._parse_pwm(data))
                else:
                    extracted_data["pwm"].append(self._parse_pwm(None))

        elif actuator_name.startswith("LED"):
            led_number = int(actuator_name[-1])
            data = self._parse_led(actuator_data.get("data", []))
            extracted_data[f"led{led_number}"].append(data)

        elif actuator_name.startswith("MOTOR"):
            pass

        elif actuator_name.startswith("BUZZER"):
            buzzer_number = int(actuator_name[-1])
            data = self._parse_buzzer(actuator_data.get("data", []))
            extracted_data[f"buzzer{buzzer_number}"].append(data)

        elif actuator_name == "CODE":
            data = self._parse_codes(actuator_data.get("data", []))
            extracted_data["codes"].append(data)

        setting_data[f"receiver_{receiver_idx}"] = extracted_data
        setting_data["sender"] = {}
        return setting_data

    def parse_simulation_value(self, actuator_data):
        """
        Parses the simulation value data.

        Args:
            actuator_data (str): The JSON string containing the actuator data.

        Returns:
            int: The parsed value.
        """
        if not isinstance(actuator_data, dict):
            return 0

        if actuator_data:
            actuator_type = 0
        actuator_name = actuator_data.get("actuator", "")
        prefix = actuator_name.rstrip("0123456789")  # Extract prefix

        index = 1
        suffix = actuator_name[len(prefix):]
        if suffix.isdigit():
            index = int(suffix)

        if prefix == "CODE":
            actuator_type = Devices.CODE_EXEC
        else:
            base = getattr(Devices, f"{prefix}_1", None)
            if base is not None:
                actuator_type = base + index - 1

        data = actuator_data.get("set_value", [])

        if data:
            data = self._get_events_id(actuator_type, data)
            return data[0]
        return 0

    def parse_simulation_receiver(self, actuator_data):
        if not isinstance(actuator_data, dict):
            return 0

        return actuator_data.get("receiver", 0)


# eg. for testing
'''
import ujson
data_parser = DataParser()
data_parser.set_slaver_idx(PARSER_RECEIVE1)
filename = 'bbl/test.json'
try:
    with open(filename, 'r') as f:
        file_data = f.read()
        data = ujson.loads(file_data)
        parse_data = data_parser.parse(data)
        print(parse_data['receiver_1'])
        #print(parse_data['sender']['deadzones'], parse_data['sender']['mid_values'])
except OSError as e:
    print('parser failed', e)
'''

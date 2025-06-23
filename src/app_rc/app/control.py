# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

from machine import Timer
from devices import Devices
from bbl import *
from machine import Pin
from parser import DataParser
import utime
import ulogger

logger = ulogger.Logger()


class ButtonHandler:
    """
    A class to handle button events.
    """

    def __init__(self):
        """
        Initializes the ButtonHandler instance.

        Args:
            None
        """
        self.buttons = {
            "button1": {
                "LONG_THR": 1000
            },
            "button2": {
                "LONG_THR": 1000
            },
            "button3": {
                "LONG_THR": 1000
            },
            "button4": {
                "LONG_THR": 1000
            },
        }
        self.buttons_long_callback = None
        self.buttons_short_callback = None
        self.buttons_press_down_callback = None
        self.buttons_release_callback = None

    def set_long_threshold(self, button_name, new_threshold):
        """
        Update the long press threshold for a specified button.

        Args:
            button_name: Name of the button to update, as a string.\
                Must be one of "button1", "button2", "button3", or "button4".
            new_threshold: New long press time threshold value, as an integer.\
                Must be a non-negative value representing milliseconds (ms).
        Example:
            >>> # Update the long press threshold for button1
            >>> update_threshold(init_config, "button1", 1500)
        """
        if button_name in self.buttons:
            self.buttons[button_name]['LONG_THR'] = new_threshold
            print("Button {} long press threshold updated to {}.".format(
                button_name, new_threshold))
        else:
            print(f"Button {button_name} does not exist.")

    def long_callback_register(self, callback):
        """
        Registers a callback for long button presses.

        Args:
            callback (function): The callback function.
        """
        self.buttons_long_callback = callback

    def short_callback_register(self, callback):
        """
        Registers a callback for short button presses.

        Args:
            callback (function): The callback function.
        """
        self.buttons_short_callback = callback

    def press_down_callback_register(self, callback):
        """
        Registers a callback for button press downs.

        Args:
            callback (function): The callback function.
        """
        self.buttons_press_down_callback = callback

    def release_callback_register(self, callback):
        """
        Registers a callback for button releases.

        Args:
            callback (function): The callback function.
        """
        self.buttons_release_callback = callback

    def check_buttons(self, buttons_value_list):
        """
        Checks the button states and triggers callbacks as needed.

        Args:
            value (list): A list of button states.
        """
        if not isinstance(buttons_value_list, list):
            raise ValueError("[BTN]buttons_value_list must be a list")
        if len(buttons_value_list) != len(self.buttons):
            raise ValueError(
                "[BTN]The length must match the number of buttons")

        for i, (button_name, button_config) in enumerate(self.buttons.items()):
            button_state = buttons_value_list[i]

            # Check if the button is pressed
            if button_state == 0:
                if "pressed_time" not in button_config:
                    button_config["pressed_time"] = utime.ticks_ms()
                    # print("press down")
                    self.buttons_press_down_callback(i)
                else:
                    press_duration = utime.ticks_ms(
                    ) - button_config["pressed_time"]
                    if press_duration >= button_config[
                            "LONG_THR"] and not button_config.get(
                                "long_pressed", False):
                        # print("long_press:", press_duration, "(ms)")
                        self.buttons_long_callback(i)
                        button_config["long_pressed"] = True
            else:
                if "pressed_time" in button_config:
                    # Calculate the duration of key presses
                    press_duration = utime.ticks_ms(
                    ) - button_config["pressed_time"]
                    # print("press release")
                    self.buttons_release_callback(i)
                    del button_config["pressed_time"]
                    # Reset long press status
                    button_config["long_pressed"] = False

                    # Check if it is a long press event
                    if press_duration >= button_config["LONG_THR"]:
                        pass
                    else:
                        # print("short_press_callback")
                        self.buttons_short_callback(i)


class PermissionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PermissionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, logger=print):
        if not hasattr(self, '_initialized'):
            self.devices: dict[str, dict] = {}
            self.logger = logger  # Logger for output messages
            self._initialized = True  # Mark the instance as initialized

    def add_permission(self, device_name: str, permission: str) -> bool:
        """
        Add a new permission level to a specific device.

        :param device_name: Name of the device.
        :param permission: Permission level to add.
        :return: True if the permission is added successfully,
                 False if it already exists.
        """
        if device_name not in self.devices:
            self.logger(f"Device '{device_name}' not registered.")
            return False

        device_permissions = self.devices[device_name]['permissions']
        if permission in device_permissions:
            self.logger(f"'{permission}' already exists in '{device_name}'.")
            return False
        device_permissions.append(permission)
        return True

    def set_permission_order(self, device_name: str,
                             permissions: List[str]) -> bool:
        """
        Set the permission order for a specific device.

        :param device_name: Name of the device.
        :param permissions: List of permission levels in desired order.
        :return: True if order is set successfully, False otherwise.
        """
        if device_name not in self.devices:
            self.logger(f"Device '{device_name}' not registered.")
            return False

        if len(permissions) < 1:
            self.logger("Permission levels cannot be empty.")
            return False

        self.devices[device_name]['permissions'] = permissions
        self.logger(f"Order for device '{device_name}' to {permissions}.")
        return True

    def register_device(self, device_name: str,
                        initial_permission: str = 'permission1') -> bool:
        """
        Register a device and initialize its permission level.

        :param device_name: Name of the device to register.
        :param initial_permission:
            The initial permission to assign to the device.
        :return: True if registration is successful, False otherwise.
        """
        if device_name in self.devices:
            self.logger(f"Device '{device_name}' already registered.")
            return False

        self.devices[device_name] = {
            'permissions': [initial_permission],
            'current_permission': initial_permission
        }
        self.logger(f"'{device_name}' registered '{initial_permission}'.")
        return True

    def set_device_permission(self, device_name: str, permission: str) -> bool:
        """
        Set the permission level for a specific device.

        :param device_name: Name of the device.
        :param permission: Permission level to set.
        :return: True if permission is set successfully, False otherwise.
        """
        if device_name not in self.devices:
            self.logger(f"Device '{device_name}' not registered.")
            return False
        if permission not in self.devices[device_name]['permissions']:
            self.logger(f"Invalid '{permission}' for device '{device_name}'.")
            return False

        self.devices[device_name]['current_permission'] = permission
        self.logger(f"'{device_name}' set to '{permission}'.")
        return True

    def get_device_permission(self, device_name: str) -> str:
        """
        Get the current permission level of a specific device.

        :param device_name: Name of the device.
        :return: Permission level of the device, or None if not registered.
        """
        if device_name not in self.devices:
            self.logger(f"Device '{device_name}' not registered.")
            return None
        return self.devices[device_name]['current_permission']

    def request_permission(self, device_name: str, permission: str) -> bool:
        """
        Request a permission for a specific device.

        :param device_name: Name of the device.
        :param permission: Permission level to request.
        :return: True if the requested permission is higher than the current
        """
        if device_name not in self.devices:
            self.logger(f"Device '{device_name}' not registered.")
            return False
        if permission not in self.devices[device_name]['permissions']:
            self.logger(f"Invalid '{permission}' for device '{device_name}'.")
            return False

        cur_p = self.devices[device_name]['current_permission']
        current_index = self.devices[device_name]['permissions'].index(cur_p)
        req_idx = self.devices[device_name]['permissions'].index(permission)

        # Return True if requested permission is greater than the current one
        return req_idx == current_index


class CycleList:
    """
    A class to manage a list of items in a cyclic manner.
    Attributes:
        items_list (list): A list of lists containing items to cycle through.
        index_list (list): A list of indices corresponding to each list
        in items_list.
    """

    def __init__(self,
                 items1=[],
                 items2=[],
                 items3=[],
                 items4=[],
                 items5=[],
                 items6=[],
                 items7=[],
                 items8=[]):
        self.items_list = [
            items1, items2, items3, items4, items5, items6, items7, items8
        ]
        self.index_list = [0, 0, 0, 0, 0, 0, 0, 0]

    def get_next_item(self, index):
        if not isinstance(index, int) or index < 0 or index >= len(
                self.items_list):
            logger.warn("[CTRL]Index out of range")
            return 0
        if self.items_list[index] == []:  # Avoid setting values to empty
            logger.warn("[CTRL]Items may be a non-empty list")
            return 0

        item = self.items_list[index][self.index_list[index]]
        self.index_list[index] = (self.index_list[index] + 1) % len(
            self.items_list[index])
        return item

    def get_items(self, index):
        if not isinstance(index, int) or index < 0 or index >= len(
                self.items_list):
            logger.warn("[CTRL]Index out of range")
            return []
        return self.items_list[index]

    def set_items(self, index, items):
        if not isinstance(index, int) or index < 0 or index >= len(
                self.items_list):
            logger.warn("[CTRL]Index out of range")
            return
        # if not isinstance(items, list) or not items:
        #     print("[CTRL]Items must be a non-empty list")
        #     return

        self.items_list[index] = items
        self.index_list[index] = 0  # Reset index when setting new items

    def set_index(self, index, list_index):
        if not isinstance(index, int) or index < 0 or index >= len(
                self.items_list):
            logger.warn("[CTRL]Index out of range")
            return
        if not isinstance(list_index,
                          int) or list_index < 0 or list_index >= len(
                              self.items_list[index]):
            logger.warn("[CTRL]List index out of range")
            return

        self.index_list[index] = list_index % len(self.items_list[index])


class ServosControllerExecMapper(ServosController):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ServosControllerExecMapper, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.singleton = ServosController()
        self.dev_manager = PermissionManager(logger.debug)
        self._has_permission = False

    def _permission_handle(self):
        if self._has_permission is False:
            self.dev_manager.set_device_permission('SERVO', 'EXEC')
            self._has_permission = True
        return

    def set_angle(self, servo_idx, angle):
        self._permission_handle()
        return self.singleton.set_angle(servo_idx, angle)

    def set_angle_stepping(self, servo_idx, angle, step_speed=None):
        self._permission_handle()
        return self.singleton.set_angle_stepping(servo_idx, angle, step_speed)

    def set_angle_step(self, servo_idx, step_speed=100):
        self._permission_handle()
        return self.singleton.set_angle_step(servo_idx, step_speed)

    def reset_info(self, servo_idx, angle, radPSec=4, call_freq=100):
        self._permission_handle()
        return self.singleton.reset_info(servo_idx, angle, radPSec, call_freq)

    def set_speed(self, servo_idx, speed_percentage):
        self._permission_handle()
        return self.singleton.set_speed(servo_idx, speed_percentage)

    def set_duty(self, servo_idx, duty):
        self._permission_handle()
        return self.singleton.set_duty(servo_idx, duty)

    def stop(self, servo_idx):
        self._permission_handle()
        return self.singleton.stop(servo_idx)


class MotorsControllerExecMapper(MotorsController):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MotorsControllerExecMapper, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.singleton = MotorsController()
        self.dev_manager = PermissionManager(logger.debug)
        self._has_permission = False

    def set_speed(self, motor_idx, speed):
        if self._has_permission is False:
            self.dev_manager.set_device_permission('MOTOR', 'EXEC')
            self._has_permission = True
        return self.singleton.set_speed(motor_idx, speed)

    def stop(self, motor_idx):
        if self._has_permission is False:
            self.dev_manager.set_device_permission('MOTOR', 'EXEC')
            self._has_permission = True
        return self.singleton.stop(motor_idx)

    def set_forward_rate(self, motor_idx, val):
        return self.singleton.set_forward_rate(motor_idx, val)

    def set_reverse_rate(self, motor_idx, val):
        return self.singleton.set_reverse_rate(motor_idx, val)

    def set_offset(self, motor_idx, val):
        return self.singleton.set_offset(motor_idx, val)

    def get_forward_rate(self, motor_idx):
        return self.singleton.get_forward_rate(motor_idx)

    def get_reverse_rate(self, motor_idx):
        return self.singleton.get_reverse_rate(motor_idx)

    def get_offset(self, motor_idx):
        return self.singleton.get_offset(motor_idx)


class BBL_Controller:

    def __init__(self):
        self.parser = DataParser()
        self.servos_mapper = ServosControllerExecMapper()
        self.motors_mapper = MotorsControllerExecMapper()
        self.servos = ServosController()
        self.motors = MotorsController()
        self.button_handler = ButtonHandler()
        self.led1 = LEDController("LED1")
        self.led2 = LEDController("LED2")
        self.buzzer1 = MusicController("BUZZER1")
        self.buzzer2 = MusicController("BUZZER2")
        self.executor = CommandExecutor(None,
                                        logger.debug,
                                        logger.info,
                                        logger.warn,
                                        logger.error)

        self.dev_manager = PermissionManager(logger.info)
        self.dev_manager.register_device('MOTOR', 'BEHAVIOR')
        self.dev_manager.register_device('SERVO', 'BEHAVIOR')
        self.dev_manager.set_permission_order('MOTOR',
                                              ['EXEC', 'EVENT', 'BEHAVIOR'])
        self.dev_manager.set_permission_order('SERVO',
                                              ['EXEC', 'EVENT', 'BEHAVIOR'])


        code_exec_danger_cmds = [
            'exit', 'quit', 'sys.exit', 'os.system', '__import__', 'open',
            'eval', 'exec', 'subprocess', 'os.remove', 'os.rmdir'
        ]
        code_exec_default_cmds = [
            'import uasyncio as asyncio',
            'from control import MotorsControllerExecMapper',
            'from control import ServosControllerExecMapper'
        ]
        code_exec_remap_rules = {
            "bbl.servos": "control",
            "bbl.buzzer": "control",
            "bbl.leds": "control",
            "bbl.motors": "control",
            "MotorsController": "MotorsControllerExecMapper",
            "ServosController": "ServosControllerExecMapper",
        }
        self.executor.register_danger_cmds(code_exec_danger_cmds)
        self.executor.register_default_cmds(code_exec_default_cmds)
        self.executor.register_remap_rules(code_exec_remap_rules)
        self.executor.register_final_cb(self._executor_final_cb)

        self.d_ch_map = [None] * 2  # LED or Buzzer channel map

        self.setting = {}
        self.receiver_index = 0
        self.enable_advanced_motor_control = [False] * 2

        self.tracker_accel_default_value = [1] * 2
        self.tracker_low_speed_zone_pctg = [0] * 2
        self.tracker_high_speed_zone_pctg = [0] * 2
        self.high_speed_duration = [1] * 2

        self.servos_effect_data_list = [0] * 4
        self.motors_effect_speed_list = [0] * 2

        self.adc_deadzone_list = [200] * 6
        self.adc_mid_list = [2048] * 6

        self._timer_init()

        self.button_handler.long_callback_register(self._button_long_cb)
        self.button_handler.short_callback_register(self._button_short_cb)
        self.button_handler.press_down_callback_register(self._button_press_cb)
        self.button_handler.release_callback_register(self._button_up_cb)

        self.key_short_effects_list = [CycleList()] * 4
        self.key_long_effects_list = [CycleList()] * 4
        self.key_down_effects_list = [CycleList()] * 4
        self.key_up_effects_list = [CycleList()] * 4
        self.adc_equal_effects_list = [CycleList()] * 6
        self.adc_above_effects_list = [CycleList()] * 6
        self.adc_below_effects_list = [CycleList()] * 6
        # 6 ADC control lever channels: items:"equal", "above", "below"
        self.analog_cmp_mid = ["equal"] * 6

        self.adv_ctrl_elapsed_time = [0] * 6
        self.adv_ctrl_last_tar_speed = [0] * 6
        self.adv_last_rc_data = [0] * 6
        self.adv_cur_rc_data = [2048] * 6
        self.cycle_time = 0.02
        self.update_tar_speed_threshold = 200

        self.en_simulation_time = 0
        self.motors_simulation_speed = [0] * 2
        self.servo_simulation_data = [0] * 4

        self.board_key = Pin(9, Pin.IN)

    def update_setting(self, setting):
        self.setting = setting
        self._update_advanced_config()

        recv_info = self.setting.get(f"receiver_{self.receiver_index}", {})
        if recv_info is {}:
            return

        leds_map = [self.led1, self.led2]
        buzzers_map = [self.buzzer1, self.buzzer2]

        for i in range(2):
            if recv_info.get(f"led{i + 1}", []) != []:
                self.d_ch_map[i] = leds_map[i]
                self.d_ch_map[i].reinit()
                self.d_ch_map[i].set_led_effect(0, 0, 0, 15, 0x000000)
            elif recv_info.get(f"buzzer{i + 1}", []) != []:
                self.d_ch_map[i] = buzzers_map[i]
                self.d_ch_map[i].reinit()
                # tune = "Converted:d=16,o=6,b=125:g5,c6,e5,8g6,e6,8g6"
                # self.d_ch_map[i].play(tune, 5, False)
            else:
                self.d_ch_map[i] = None

        for i in range(4):
            pwm_info = None
            pwms_info = recv_info.get("pwm", [[], [], [], []])
            pwm_info = pwms_info[i]
            if len(pwm_info) > 1:
                self.servos.reset_info(i+1, pwm_info[0])
                self.servos.set_angle_step(i+1, pwm_info[1])

        try:
            for i in range(2):
                offset, min_val, max_val = recv_info.get("motor", [])[i]
                self.motors.set_forward_rate(i+1, max_val)
                self.motors.set_reverse_rate(i+1, min_val)
                self.motors.set_offset(i+1, offset)
        except (Exception) as e:
            logger.warn(f"[CTRL]UPDATE_MOTORS_PARAM: {e}")

        for i in range(6):
            self.adc_mid_list[i] = self.setting.get("sender", {}).get(
                "mid_values", []
            )[i] if "sender" in self.setting and "mid_values" in self.setting[
                "sender"] else self.adc_mid_list[i]
            self.adc_deadzone_list[i] = self.setting.get("sender", {}).get(
                "deadzones", []
            )[i] if "sender" in self.setting and "deadzones" in self.setting[
                "sender"] else self.adc_deadzone_list[i]

    def set_slaver_idx(self, idx):
        self.receiver_index = idx

    def _timer_init(self):
        self.timer0 = Timer(0)
        self.timer0.init(period=1,
                         mode=Timer.PERIODIC,
                         callback=self.timer0_callback)
        self.tim0_div_cnt = 0

    def adc_value_deal(self, x, max=4096, mid=2048, dz=200):

        def convert(x, i_min, i_max, o_min, o_max):
            return (x - i_min) * (o_max - o_min) / (i_max - i_min) + o_min

        if mid - dz <= x <= mid + dz:
            return 0

        m_mid = max / 2

        if x <= mid:
            x = convert(x, 0, mid - dz, -m_mid, 0)
        elif x > mid:
            x = convert(x, mid + dz, max, 0, m_mid)
        return x

    def _handle_effect(self, effect, setting, mode="normal", recv=None):
        logger.info(f"[CTRL][{mode.upper()}]EFFECT: {effect}")

        recv_idx = recv if recv is not None else self.receiver_index

        if not isinstance(effect, int):
            logger.error(f"[CTRL][{mode.upper()}] Type error, need int")
            return

        event_dic = self.parser.parse_event_id(effect)
        effect_actor_idx = event_dic["actuator"]
        effect_actor_val = event_dic["value"]

        # MOTORS
        if effect_actor_idx in [Devices.MOTOR_1, Devices.MOTOR_2]:
            motor_idx = effect_actor_idx
            effect_value = effect_actor_val
            if mode == "simulation":
                self.motors_simulation_speed[motor_idx - 1] = 2047 * effect_value / 100
                self._en_simulation_loop('MOTOR', True)
            else:
                self.motors_effect_speed_list[motor_idx - 1] = 2047 * effect_value / 100

        # LEDS
        elif effect_actor_idx in [Devices.LED_1, Devices.LED_2]:
            number = effect_actor_idx - 2
            effect_value = effect_actor_val
            led_events = setting[f"receiver_{recv_idx}"].get(f"led{number}", [])

            for effect, sequence_number, mode, rgb_value, repeat_times, time in led_events:
                if effect == effect_value:
                    led = self.led1 if number == 1 else self.led2
                    led.set_led_effect(mode, time * 1000, repeat_times, sequence_number, rgb_value)

        # SERVOS
        elif Devices.PWM_1 <= effect_actor_idx <= Devices.PWM_4:
            pwm_idx = effect_actor_idx - 4
            pwm_config = setting.get(f"receiver_{recv_idx}", {}).get("pwm", [])

            if pwm_idx - 1 < len(pwm_config):
                bias, vel, min_value, max_value, pwm_type = pwm_config[pwm_idx - 1]
            else:
                raise IndexError(f"pwm_idx {pwm_idx} is out of range for receiver_{recv_idx}.")

            effect_value = effect_actor_val
            if pwm_type == "speed":
                effect_value = effect_value * 10 + 0
            elif pwm_type == "angle":
                effect_value = effect_value * 10 + 1

            if mode == "simulation":
                self.servo_simulation_data[pwm_idx - 1] = effect_value
                self._en_simulation_loop('SERVO', True)
            else:
                self.servos_effect_data_list[pwm_idx - 1] = effect_value

        # BUZZERS
        elif effect_actor_idx in [Devices.BUZZER_1, Devices.BUZZER_2]:
            buzzer_idx = effect_actor_idx - 8
            self._buzzer_effect_trig(buzzer_idx, effect_actor_val, setting)

        # CODE
        elif effect_actor_idx == Devices.CODE_EXEC:
            self._code_effect_trig(effect_actor_val, setting)

    def analog_effect_cb(self, index, effect_type):
        try:
            effects = self.setting["sender"][f"adc_ch{index + 1}"][effect_type]
            if effects:
                logger.info(f"[CTRL]ANALOG_CH:{index} {effect_type}:{effects}")
        except Exception:
            return

        effect_list_map = {
            "equal_mid": self.adc_equal_effects_list,
            "above_mid": self.adc_above_effects_list,
            "below_mid": self.adc_below_effects_list
        }

        effect_list = effect_list_map.get(effect_type)
        if not effect_list:
            return

        for effects_index, effect_arr in enumerate(effects):
            org_effect = effect_list[index].get_items(effects_index)
            if org_effect != effect_arr:
                effect_list[index].set_items(effects_index, effect_arr)
            effect = effect_list[index].get_next_item(effects_index)
            self._handle_effect(effect, self.setting)

    def _analog_equal_mid_cb(self, index):
        self.analog_effect_cb(index, "equal_mid")

    def _analog_above_mid_cb(self, index):
        self.analog_effect_cb(index, "above_mid")

    def _analog_below_mid_cb(self, index):
        self.analog_effect_cb(index, "below_mid")

    def _button_effect_cb(self, btn_idx, effect_type):
        try:
            effects = self.setting["sender"][f"key{btn_idx + 1}"][effect_type]
            if effects:
                logger.info(f"[CTRL]BTN:{btn_idx} {effect_type}:{effects}")
        except Exception:
            return

        effect_list_map = {
            "long": self.key_long_effects_list,
            "short": self.key_short_effects_list,
            "down": self.key_down_effects_list,
            "release": self.key_up_effects_list
        }

        effect_list = effect_list_map.get(effect_type)
        if not effect_list:
            return

        for effects_index, effect_arr in enumerate(effects):
            org_effect = effect_list[btn_idx].get_items(effects_index)
            if org_effect != effect_arr:
                effect_list[btn_idx].set_items(effects_index, effect_arr)
            effect = effect_list[btn_idx].get_next_item(effects_index)
            self._handle_effect(effect, self.setting)

    def _button_long_cb(self, btn_idx):
        self._button_effect_cb(btn_idx, "long")

    def _button_short_cb(self, btn_idx):
        self._button_effect_cb(btn_idx, "short")

    def _button_press_cb(self, btn_idx):
        self._button_effect_cb(btn_idx, "down")

    def _button_up_cb(self, btn_idx):
        self._button_effect_cb(btn_idx, "release")

    def _update_advanced_config(self):
        """
        Apply advanced configuration settings based on the receiver index.
        """
        adv_config_list = self.setting.get(f"receiver_{self.receiver_index}",
                                           {}).get("advanced_config", None)
        if adv_config_list is None:
            logger.warn("[CTRL]advanced config list is empty in setting.")
            return

        for item in adv_config_list:
            if len(item) != 6:
                logger.error("[CTRL]Invalid item in config_list.")
                return

            (num, en, tracker_accel, tracker_low_speed_zone_pctg,
             tracker_high_speed_zone_pctg, high_speed_duration) = item
            if en and (1 <= num <= 2):
                self.tracker_accel_default_value[num - 1] = \
                    tracker_accel
                self.tracker_low_speed_zone_pctg[num - 1] = \
                    tracker_low_speed_zone_pctg
                self.tracker_high_speed_zone_pctg[num - 1] = \
                    tracker_high_speed_zone_pctg
                self.high_speed_duration[num - 1] = \
                    high_speed_duration
                self.enable_advanced_motor_control[num - 1] = True
            else:
                if (num == 1):
                    self.enable_advanced_motor_control[0] = False
                elif (num == 2):
                    self.enable_advanced_motor_control[1] = False

    def motor_speed_calculate(self, rc_data, motor_index):
        if self.setting is None or rc_data is None:
            logger.warn("[CTRL]Settings or RC data cannot be None")
            return 0

        bias = self.motors.get_offset(motor_index)
        min_value = self.motors.get_reverse_rate(motor_index)
        max_value = self.motors.get_forward_rate(motor_index)

        bias = bias * 2048 / 100
        motors_control = self.setting["sender"].get(f"m{motor_index}", [])

        if motors_control is [] or not isinstance(motors_control, list):
            return 0

        rc_value = 0
        for channel, direction in motors_control:
            # advance control (hign zone)
            if self.enable_advanced_motor_control[motor_index - 1] is True:
                if abs(rc_data[channel]) <= abs(
                        self.adv_last_rc_data[channel]):
                    lite_rc_data = rc_data[channel]
                else:
                    lite_rc_data = self.adv_last_rc_data[channel]
                self.adv_cur_rc_data[channel], \
                    self.adv_ctrl_last_tar_speed[channel], \
                    self.adv_ctrl_elapsed_time[channel] = \
                    self.high_speed_zone_map_handler(
                        motor_index - 1,
                        self.adv_cur_rc_data[channel],
                        lite_rc_data,
                        self.adv_ctrl_last_tar_speed[channel],
                        self.adv_ctrl_elapsed_time[channel],
                        True)

                self.adv_last_rc_data[channel] = rc_data[channel]
                rc_value += self.adv_cur_rc_data[channel] * direction
            else:
                rc_value += rc_data[channel] * direction

        if (rc_value + bias >= 0):
            motor_speed = (int)((rc_value + bias) * max_value / 100)
            motor_speed = self.get_valid_value(motor_speed, -2047, 2047)
            return int(abs(motor_speed))
        else:
            motor_speed = (int)((rc_value + bias) * min_value / 100)
            motor_speed = self.get_valid_value(motor_speed, -2047, 2047)
            return int(-abs(motor_speed))

    def _servo_handler(self, rc_data, pwm_index):
        bias, speed, min_value, max_value, pwm_type = self.setting[
            f"receiver_{self.receiver_index}"]["pwm"][pwm_index - 1]

        # bias = bias * 2048 / 100

        pwm_control = self.setting["sender"][f"p{pwm_index}"]

        if pwm_control == []:  # is angle servo
            return self.servos_effect_data_list[pwm_index - 1]
        if rc_data is None or self.setting is None:  # is speed servo
            return 0

        rc_value = 0
        for channel, direction in pwm_control:
            rc_value += rc_data[channel] * direction

        if pwm_type == "speed":
            if rc_value <= 0:
                rc_value = rc_value * min_value / 2048
            else:
                rc_value = rc_value * max_value / 2048
            rc_value = self.get_valid_value(rc_value, -100, 100)
            rc_value = (round(rc_value)) * 10 + 0
        elif pwm_type == "angle":
            rc_value = (rc_value * (max_value - min_value) /
                        4096) + (max_value + min_value) / 2
            rc_value = self.get_valid_value(rc_value, 0, 180)
            rc_value = (round(rc_value)) * 10 + 1
        return int(rc_value)

    def _buzzer_effect_trig(self, buzzer_idx, song_idx, setting):
        if not 1 <= buzzer_idx < 3:
            logger.error(f"[CTRL]Invalid buzzer index:{buzzer_idx}")
            return
        recv_info = setting.get(f"receiver_{self.receiver_index}", {})
        songs = recv_info.get(f"buzzer{buzzer_idx}", [])
        for song in songs:
            if song[0] == song_idx:
                loop_en = False if song[2] != 255 else True
                tune = song[3]
                volume = song[1]
                if buzzer_idx == 1:
                    self.buzzer1.play(tune, volume, False, loop_en)
                elif buzzer_idx == 2:
                    self.buzzer2.play(tune, volume, False, loop_en)
                logger.debug(f"[CTRL]Buzzer{buzzer_idx}: {song}")
                return

    def _code_effect_trig(self, code_idx, setting):
        recv_info = setting.get(f"receiver_{self.receiver_index}", {})
        codes = recv_info.get("codes", [])
        for code in codes:
            if code[0] == code_idx:
                cmd = code[1]
                self.executor.run(cmd)
                return

    def handler(self, setting, index, remote_data):
        if index == 0:
            logger.error(f"[CTRL]KeyError: receiver_{index}")
            return
        self.receiver_index = index

        if setting == {} or (not isinstance(setting, dict)):
            return

        if setting != self.setting:
            self.update_setting(setting)

        for i in range(6):
            remote_data[i] = self.adc_value_deal(
                remote_data[i],
                4096,
                self.adc_mid_list[i],
                self.adc_deadzone_list[i]
            )

        # Trigger median event
        for ch_idx in range(6):
            if remote_data[ch_idx] == 0 and self.analog_cmp_mid[
                    ch_idx] != "equal":
                self._analog_equal_mid_cb(ch_idx)
                self.analog_cmp_mid[ch_idx] = "equal"
            elif remote_data[ch_idx] < 0 and self.analog_cmp_mid[
                    ch_idx] != "below":
                self._analog_below_mid_cb(ch_idx)
                self.analog_cmp_mid[ch_idx] = "below"
            elif remote_data[ch_idx] > 0 and self.analog_cmp_mid[
                    ch_idx] != "above":
                self._analog_above_mid_cb(ch_idx)
                self.analog_cmp_mid[ch_idx] = "above"

        if self.dev_manager.request_permission('MOTOR', 'BEHAVIOR'):
            for motor_idx in range(1, 3):
                res_speed = 0
                if self.setting["sender"][f"m{motor_idx}"] == []:
                    # If it is not for behavioral control
                    res_speed = self.motors_effect_speed_list[motor_idx - 1]
                else:
                    # If it's behavioral control
                    _speed = self.motor_speed_calculate(remote_data, motor_idx)
                    if self.enable_advanced_motor_control[motor_idx-1] is True:
                        res_speed = self.nonlinear_map(
                            _speed, 0,
                            self.tracker_low_speed_zone_pctg[motor_idx-1]/100,
                            self.tracker_accel_default_value[motor_idx-1])
                    else:
                        res_speed = _speed
                self.motors.set_speed(motor_idx, res_speed)

        if self.dev_manager.request_permission('SERVO', 'BEHAVIOR'):
            for i in range(1, 5):
                effect = self._servo_handler(remote_data, i)
                is_angle_servo = effect % 10
                if is_angle_servo == 1:
                    self.servos.set_angle_stepping(i, (int)(effect / 10))
                elif is_angle_servo == 0:
                    self.servos.set_speed(i, (int)(effect / 10))

        self.button_handler.check_buttons(remote_data[6:])

    def stop(self, permission=None):
        if permission is None:
            self.servos_effect_data_list = [0] * 4
            self.motors_effect_speed_list = [0] * 2

            for i in range(1, 3):
                self.motors.stop(i)
            for i in range(1, 5):
                self.servos.stop(i)
            return

        if self.dev_manager.request_permission('MOTOR', permission):
            speed_map = {
                'BEHAVIOR': self.motors_effect_speed_list,
                'EVENT': self.motors_simulation_speed
            }
            for i in range(1, 3):
                speed_map[permission][i-1] = 0
                self.motors.stop(i)

        if self.dev_manager.request_permission('SERVO', permission):
            speed_map = {
                'BEHAVIOR': self.servos_effect_data_list,
                'EVENT': self.servo_simulation_data
            }
            for i in range(1, 5):
                speed_map[permission][i-1] = 0
                self.servos.stop(i)

    def reinit(self, permission=None):
        self.stop(permission)

        self.setting = {}
        self.servos_effect_data_list = [0] * 4
        self.motors_effect_speed_list = [0] * 2
        self.servo_simulation_data = [0] * 4
        self.motors_simulation_speed = [0] * 2

        for dev in self.d_ch_map:
            if dev is not None:
                dev.reinit()
            if (dev is self.led1) or (dev is self.led2):
                # If it is LED, the light off effect needs to be set
                dev.set_led_effect(0, 0, 0, 15, 0x000000)

    def get_valid_value(self, value, min_val, max_val):
        return min(max(value, min_val), max_val)

    def timer0_callback(self, timer):
        self.motors.motors_period_cb()

        for dev in self.d_ch_map:
            if dev is not None:
                dev.timing_proc()

        if self.tim0_div_cnt == 0:
            self.servos.timing_proc()

        self.tim0_div_cnt = (self.tim0_div_cnt + 1) % 10

    def _high_speed_map(self,
                        current_speed,
                        target_speed,
                        elapsed_time,
                        total_time=2.0,
                        cycle_time=0.02):

        def limit_value(value):
            HIGHT_ZONE_MIN_SPEED = 800
            if value < -HIGHT_ZONE_MIN_SPEED or value > HIGHT_ZONE_MIN_SPEED:
                return value
            elif value < 0:
                return -HIGHT_ZONE_MIN_SPEED
            else:
                return HIGHT_ZONE_MIN_SPEED

        remaining_time = total_time - elapsed_time  # Calculate remaining time

        c_speed = abs(current_speed)
        t_speed = abs(target_speed)

        # If the remaining time is less than the cycle time
        # set it directly as the target speed
        if remaining_time < cycle_time:
            return target_speed

        if t_speed <= c_speed:
            return target_speed

        # Calculate the rate of change in speed
        speed_change_rate = (t_speed - c_speed) / remaining_time

        # Calculate the speed change within the current cycle
        speed_change_this_cycle = speed_change_rate * cycle_time

        # Calculate new speed
        new_speed = c_speed + speed_change_this_cycle

        new_speed = limit_value(new_speed)

        return new_speed if target_speed >= 0 else -new_speed

    def _low_speed_map(self, value, start, end, rate):
        # Ensure that the input value is within the specified range
        if value <= start + 1:
            return 0
        elif value >= end:
            return 2047

        mapped_value = rate * ((value - start)**2) / (2 * (end - start))
        # mapped_value = rate * math.log(value - start) * (end - start)
        return int(mapped_value)

    def high_speed_zone_map_handler(self,
                                    motor_idx,
                                    current_speed,
                                    target_speed,
                                    last_tar_speed,
                                    elapsed_time,
                                    en):
        if en is True:
            if abs(
                    last_tar_speed - target_speed
            ) > self.update_tar_speed_threshold or elapsed_time > \
                    self.high_speed_duration[motor_idx]:
                elapsed_time = 0
            if (abs(target_speed) > 2048 * (
                    1 - self.tracker_high_speed_zone_pctg[motor_idx] / 100)):
                current_speed = self._high_speed_map(
                    current_speed, target_speed, elapsed_time,
                    self.high_speed_duration[motor_idx], self.cycle_time)
            else:
                current_speed = target_speed
        else:
            current_speed = target_speed
        last_tar_speed = target_speed
        elapsed_time += self.cycle_time
        return current_speed, last_tar_speed, elapsed_time

    def nonlinear_map(self,
                      set_speed,
                      dead_zone=500,
                      low_speed_percentage=0.5,
                      linear_rate=1.5):
        THRESHOLD = 2047
        speed = abs(set_speed)
        # The output is 0 in the dead zone
        if (speed) < dead_zone:
            return 0
        if speed > THRESHOLD:
            speed = THRESHOLD

        # Calculate the threshold value for the slow phase
        low_speed_threshold = dead_zone + (
            2048 - 2 * dead_zone) * low_speed_percentage

        tracker_speed = self._low_speed_map(
            min(speed, low_speed_threshold - 1), dead_zone,
            low_speed_threshold, linear_rate)
        if speed >= low_speed_threshold:  # Medium and high speed section
            tracker_speed = tracker_speed + (speed -
                                             low_speed_threshold) * linear_rate

        tracker_speed = min(tracker_speed, THRESHOLD)
        return int(tracker_speed if set_speed >= 0 else -tracker_speed)

    def _executor_final_cb(self):
        self.dev_manager.set_device_permission('MOTOR', 'BEHAVIOR')
        self.dev_manager.set_device_permission('SERVO', 'BEHAVIOR')

    def simulation_effect_handle(self):
        # motors
        if self.dev_manager.request_permission('MOTOR', 'EVENT'):
            press_duration = utime.ticks_ms() - self.en_simulation_time
            if press_duration >= 2000:
                self._en_simulation_loop('MOTOR', False)
                logger.info("[CTRL]Simulation Motor loop end")
                return
            for index in range(1, 3):
                res_speed = self.motors_simulation_speed[index - 1]
                self.motors.set_speed(index, res_speed)

        # servos
        if self.dev_manager.request_permission('SERVO', 'EVENT'):
            press_duration = utime.ticks_ms() - self.en_simulation_time
            if press_duration >= 2000:
                self._en_simulation_loop('SERVO', False)
                logger.info("[CTRL]Simulation Servo loop end")
                return
            for i in range(1, 5):
                effect = self.servo_simulation_data[i - 1]
                is_angle_servo = effect % 10
                if is_angle_servo == 1:
                    self.servos.set_angle(i, (int)(effect / 10))
                elif is_angle_servo == 0:
                    self.servos.set_speed(i, (int)(effect / 10))

    def _en_simulation_loop(self, dev, en):
        self.en_simulation_time = utime.ticks_ms()
        if en is True:
            self.dev_manager.set_device_permission(dev, 'EVENT')
        if en is False:
            self.dev_manager.set_device_permission(dev, 'BEHAVIOR')
            if dev == 'SERVO':
                self.servo_simulation_data = [0, 0, 0, 0]
            elif dev == 'MOTOR':
                self.motors_simulation_speed = [0, 0]

    def simulation_effect_set(self, recv_idx, setting, effect):
        self._handle_effect(effect, setting, "simulation", recv_idx)

    async def executor_handle(self):
        await self.executor.block_handle()
        logger.error("[CTRL]executor loop crash.")

    def board_key_handler(self):
        if self.board_key.value() == 0:
            while self.board_key.value() == 0:
                self.servos.set_angle(1, 90)
                utime.sleep(0.01)
            self.servos.stop(1)

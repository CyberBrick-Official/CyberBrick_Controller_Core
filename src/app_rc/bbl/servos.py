# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

from machine import Pin, PWM

SERVO_CHANNEL1 = 3
SERVO_CHANNEL2 = 2
SERVO_CHANNEL3 = 1
SERVO_CHANNEL4 = 0


class ServosController:
    """
    A class to control servo motors using PWM signals.

    This class provides a simple interface to control up to four \
        servo motors connected to specific channels.
    It initializes PWM objects for each servo channel and provides \
        methods to set the duty cycle and stop the servo motors.

    Example:
        >>> servos = ServosController()
        >>> # Set servo 1 to 90 degrees
        >>> servos.set_angle(1, 90)
        >>> # Set servo 2 to 180 degrees with a step speed of 10
        >>> servos.set_angle_stepping(2, 180, 10)
        >>> # Set the speed of servo 3 to 50%
        >>> servos.set_speed(3, 50)
    """

    def __init__(self):
        """
        Initializes the ServosController instance.
        Example:
            >>> servos = ServosController()
            >>> # Initializes servos on channels 1 to 4.
        """
        self.servo1_pwm = PWM(Pin(SERVO_CHANNEL1), freq=50)
        self.servo2_pwm = PWM(Pin(SERVO_CHANNEL2), freq=50)
        self.servo3_pwm = PWM(Pin(SERVO_CHANNEL3), freq=50)
        self.servo4_pwm = PWM(Pin(SERVO_CHANNEL4), freq=50)
        self.servos_map = [
            self.servo1_pwm, self.servo2_pwm, self.servo3_pwm, self.servo4_pwm
        ]
        self.servos_info_map = [
            {"c_ang": 0, "s_ang": 0, "rh_ang": 0, "vel": 0, "step_en": False},
            {"c_ang": 0, "s_ang": 0, "rh_ang": 0, "vel": 0, "step_en": False},
            {"c_ang": 0, "s_ang": 0, "rh_ang": 0, "vel": 0, "step_en": False},
            {"c_ang": 0, "s_ang": 0, "rh_ang": 0, "vel": 0, "step_en": False},
        ]
        self.sensitity = 180
        self.tim_call_freq = 100

    def set_angle(self, servo_idx, angle):
        """
        Sets the angle of a specified servo motor.

        This method converts the angle to a corresponding duty cycle for the PWM signal.
        The angle should be between 0 and 180 degrees.

        Args:
            servo_idx (int): Index of the servo motor (1 to 4).
            angle (int): Desired angle between 0 and 180 degrees.

        Example:
            >>> # Set servo 1 to 90 degrees
            >>> servos.set_angle(1, 90)
        """
        if not 0 <= angle <= 180:
            print("[servo]Invalid angle, Must be between 0 and 180.")
            return

        duty = (int)(angle * 102 / 180 + 25)
        internal_idx = servo_idx - 1

        self.reset_info(servo_idx, angle)

        if not 0 <= internal_idx < len(self.servos_map):
            print("[servo]Invalid servo index. Must be between 1 and 4.")
            return

        self.servos_map[internal_idx].duty(duty)

    def set_angle_stepping(self, servo_idx, angle, step_speed=None):
        """
        Sets the servo to move to the target angle using stepping motions.

        The servo will gradually move to the target angle \
            at the specified speed.

        Args:
            servo_idx (int): Index of the servo motor (1 to 4).
            angle (int): Target angle between 0 and 180 degrees.
            step_speed (int, optional): \
                Speed of the movement (0-100). Higher values move faster.

        Example:
            >>> # Set servo 2 to 180 degrees with a step speed of 10
            >>> servos.set_angle_stepping(2, 180, 10)
        """
        if not 0 <= angle <= 180:
            print("[servo]Invalid angle, Must be between 0 and 180.")
            return

        internal_idx = servo_idx - 1

        if step_speed is not None:
            self.servos_info_map[internal_idx]["vel"] = step_speed

        if self.servos_info_map[internal_idx]["vel"] == 100:
            self.set_angle(servo_idx, angle)
            self.servos_info_map[internal_idx]["rh_ang"] = angle
            self.servos_info_map[internal_idx]["c_ang"] = angle
            return

        cur_angle = self.servos_info_map[internal_idx]["c_ang"]
        self.servos_info_map[internal_idx]["rh_ang"] = cur_angle
        self.servos_info_map[internal_idx]["s_ang"] = angle

        self.servos_info_map[internal_idx]["step_en"] = True

    def set_angle_step(self, servo_idx, step_speed=100):
        """
        Sets the speed of the stepping motion for a specified servo.

        Args:
            servo_idx (int): Index of the servo motor (1 to 4).
            step_speed (int): Speed of the stepping motion, from 0 to 100.

        Example:
            >>> # Set the stepping speed of servo 3 to 50%
            >>> servos.set_angle_step(3, 50)
        """
        if not 0 <= step_speed <= 180:
            print("[servo]Invalid step, Must be between 0 and 100.")
            return

        internal_idx = servo_idx - 1
        self.servos_info_map[internal_idx]["vel"] = step_speed

    def reset_info(self, servo_idx, angle, radPSec=8.05, call_freq=100):
        """
        Resets the information for a servo motor, \
            including its current angle and step configuration.

        Args:
            servo_idx (int): Index of the servo motor (1 to 4).
            angle (int): Angle to reset the servo to (0 to 180).
            radPSec (int, optional): \
                The rotational speed in radians per second (default 4).
            call_freq (int, optional): \
                Frequency at which the timing function is called (default 100).

        Example:
            >>> # Reset servo 1 to 90 degrees with default settings
            >>> servos.reset_info(1, 90)
        """
        if not 0 <= angle <= 180:
            print("[servo]Invalid angle, Must be between 0 and 180.")
            return

        internal_idx = servo_idx - 1

        if not 0 <= internal_idx < len(self.servos_info_map):
            print("[servo]Invalid servo index. Must be between 1 and 4.")
            return

        self.tim_call_freq = call_freq
        self.sensitivity = (57.3 * radPSec) / self.tim_call_freq

        self.servos_info_map[internal_idx]["step_en"] = False
        self.servos_info_map[internal_idx]["c_ang"] = angle
        self.servos_info_map[internal_idx]["rh_ang"] = angle
        self.servos_info_map[internal_idx]["s_ang"] = angle

    def set_speed(self, servo_idx, speed_percentage):
        """
        Sets the speed of the servo motor.

        The speed is specified as a percentage between -100 and 100, \
            where positive values move the servo in one direction, \
                and negative values move it in the opposite direction.

        Args:
            servo_idx (int): Index of the servo motor (1 to 4).
            speed_percentage (int): \
                Speed of the servo as a percentage (-100 to 100).

        Example:
            >>> # Set the speed of servo 2 to 50%
            >>> servos.set_speed(2, 50)
        """
        if not -100 <= speed_percentage <= 100:
            print("[servo]Invalid speed, Must be between -100 and 100.")
            return

        duty = round(speed_percentage * 51.2 / 100 + 76.8)
        internal_idx = servo_idx - 1

        if not 0 <= internal_idx < len(self.servos_map):
            print("[servo]Invalid servo index. Must be between 1 and 4.")
            return

        self.servos_map[internal_idx].duty(duty)

    def set_duty(self, servo_idx, duty):
        """
        Sets the duty cycle of a servo motor.

        This method sets the duty cycle for a specified servo motor, \
            which controls its position.
        The duty cycle is the proportion of time within a period that \
            the signal is active,
        and it ranges from 25 to 125 for most servo motors.

        Args:
            servo_idx (int): Index of the servo motor in the range [1, 4].
            duty (int): Duty cycle to set for the servo motor, ranging \
                from 25 to 125.
        Returns:
            None
        Example:
            >>> # Set the duty cycle of servo 3 to 100
            >>> servos.set_duty(3, 100)
        """
        internal_idx = servo_idx - 1

        if 0 <= internal_idx < len(self.servos_map):
            self.servos_map[internal_idx].duty(duty)
        else:
            raise ValueError(
                "[servo]Invalid servo index. Must be between 1 and 4.")

    def timing_proc(self):
        """
        Periodically checks and updates the servo motors that are in stepping mode.

        This method is called by a timer or main loop to \
            update the servo positions gradually.
        It calculates the next angle based on the velocity and \
            sensitivity settings, and applies the PWM duty cycle.

        Example:
            >>> # Call timing_proc in the main loop to update servo positions.
            >>> servos.timing_proc()
        """
        for servo_idx in range(4):
            if self.servos_info_map[servo_idx]["step_en"] is False:
                continue

            c_ang = self.servos_info_map[servo_idx]["c_ang"]
            s_ang = self.servos_info_map[servo_idx]["s_ang"]
            velocity = self.servos_info_map[servo_idx]["vel"]
            interval = s_ang - c_ang

            if interval != 0 and velocity != 0:
                angle = 0
                if interval > 0:
                    angle = c_ang + (velocity / 100 * self.sensitivity)
                    angle = angle if angle <= s_ang else s_ang
                elif interval < 0:
                    angle = c_ang - (velocity / 100 * self.sensitivity)
                    angle = angle if angle >= s_ang else s_ang
                else:
                    self.servos_info_map[servo_idx]["rh_ang"] = s_ang
                    self.servos_info_map[servo_idx]["step_en"] = False
                    continue

                self.servos_info_map[servo_idx]["c_ang"] = angle

                duty = (int)(angle * 102 / 180 + 25)
                self.servos_map[servo_idx].duty(duty)

    def stop(self, servo_idx):
        """
        Stops a servo motor by setting its duty cycle to 0.
        Args:
            servo_idx (int): Index of the servo motor (1 to 4).
        Example:
            >>> # Stop servo 1
            >>> servos.stop(1)
        """
        internal_idx = servo_idx - 1

        if 0 <= internal_idx < len(self.servos_map):
            self.servos_map[internal_idx].duty(0)
        else:
            raise ValueError(
                "[servo]Invalid servo index. Must be between 1 and 4.")

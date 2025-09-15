# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

import sys
import gc
import machine
import uasyncio
import time
import ujson
import ulogger

sys.path.append("/app")
sys.path.append("/bbl")
if '.frozen' in sys.path:
    sys.path.remove('.frozen')
    sys.path.append('.frozen')

conf_update_flag = True  # Flag to indicate configuration update is needed
setting = None           # Parsed configuration settings


async def _reload_configuration(parser, logger):
    """Helper function to reload configuration from file"""
    global conf_update_flag, setting
    conf_update_flag = False

    # Clear memory before loading
    rc_conf = None
    setting = None
    gc.collect()

    # Load configuration file
    try:
        with open('rc_config', 'r') as f:
            rc_conf = ujson.load(f)
            gc.collect()
    except Exception as e:
        logger.warn(f"[MAIN]CFG_LOAD_ERR:{e}.")
    gc.collect()

    # Parse configuration if loaded successfully
    if rc_conf is not None:
        setting = parser.parse(rc_conf)
        del rc_conf
        logger.info("[MAIN]PARSE_UPDATE")
    gc.collect()


def sleep_handler():
    import neopixel
    import machine
    import esp32

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


async def master_init():
    """Initialize the master controller and start tasks"""
    import rc_module
    from cyberbrick import sys as cbsys
    from parser import DataParser
    from sleepModule import SleepModule

    logger = ulogger.Logger()
    logger.info("[MAIN]MASTER_INIT.")

    # Initialize RC module
    if not rc_module.rc_master_init():
        return

    data_parser = DataParser()

    async def period_task():
        # Periodic task to check for config updates and reload settings
        global conf_update_flag, setting

        while True:
            # Check for file transfer updates
            if rc_module.file_transfer():
                logger.info("[MAIN]CONFIG_UPDATE.")
                await _reload_configuration(data_parser, logger)

                conf_update_flag = True

            await uasyncio.sleep(0.5)

    async def sleep_detc_task():
        # Task to monitor activity and trigger sleep mode when inactive
        global setting, conf_update_flag

        sleep_module = SleepModule(logger.info)

        # Channel configuration
        ch_names = ['L1', 'L2', 'L3', 'R1', 'R2', 'R3', 'K1', 'K2', 'K3', 'K4']
        sleep_trig_time = 5 * 60  # Default sleep trigger time: 5 minutes

        while True:
            sleep_module.enable()

            sleep_module.register_sleep_callback(sleep_handler)

            # Configure channels with appropriate thresholds
            for i in range(6):
                sleep_module.add_channel(ch_names[i], 100, sleep_trig_time)
            for i in range(6, 10):
                sleep_module.add_channel(ch_names[i], 1, sleep_trig_time)

            # Sleep detection main loop
            sleep_en = True
            # Update sleep enable status from configuration
            if setting is not None and 'sender' in setting:
                sleep_en = setting['sender'].get('sleep', {}).get('en', True)
            active = (cbsys.heartbeat_status() is cbsys.HEARTBEAT_ACTIVE)

            while True:
                # Wait for 1 second (non-blocking in uasyncio context)
                await uasyncio.sleep(1)

                # Process configuration updates
                if conf_update_flag:
                    conf_update_flag = False
                    sleep_module.disable()
                    break

                # If the “active” state changed, refresh sleep monitoring
                if active != (cbsys.heartbeat_status() is cbsys.HEARTBEAT_ACTIVE):
                    sleep_module.disable()
                    break

                if not sleep_en or active:
                    continue

                rc_data = rc_module.rc_master_data()
                if rc_data is not None:
                    for i, item in enumerate(rc_data):
                        sleep_module.register_data(ch_names[i], item)

                sleep_module.monitor_channels()

    await uasyncio.gather(period_task(), sleep_detc_task())


async def slave_init():
    import rc_module

    logger = ulogger.Logger()
    logger.info("[MAIN]SLAVE_INIT.")

    if rc_module.rc_slave_init() is False:
        return

    from control import BBL_Controller
    from parser import DataParser
    gc.collect()

    data_parser = DataParser()
    bbl_controller = BBL_Controller()

    async def period_task():
        global conf_update_flag

        while True:
            # Check for file transfer updates
            if rc_module.file_transfer():
                logger.info("[MAIN]CONFIG_UPDATE.")
                conf_update_flag = True
            await uasyncio.sleep(0.5)

    async def control_task():
        global conf_update_flag, setting
        EMPTY_DATA = [0] * 10
        rc_index = 0

        while True:
            try:
                if conf_update_flag is True:
                    bbl_controller.reinit()

                    rc_index = rc_module.rc_index()
                    data_parser.set_slave_idx(rc_index)
                    logger.info(f'[MAIN]SLAVE_IDX: {rc_index}')

                    await _reload_configuration(data_parser, logger)
                    bbl_controller.reinit()

                if rc_index != rc_module.rc_index():
                    # Must update config
                    conf_update_flag = True
                    continue

                rc_data = rc_module.rc_slave_data()
                if rc_data and setting and rc_data != EMPTY_DATA:
                    bbl_controller.handler(setting, rc_index, rc_data)
                else:
                    bbl_controller.stop('BEHAVIOR')
            except Exception as e:
                bbl_controller.reinit()
                logger.error(f"[MAIN]CRTL_TASK: {e}")
                sys.exit()
            bbl_controller.board_key_handler()
            await uasyncio.sleep(0.02)

    async def simulation_task():
        while True:
            try:
                sim_case = rc_module.rc_simulation()
                if sim_case:
                    try:
                        sim_case = ujson.loads(sim_case)
                    except Exception as e:
                        logger.error(f"[MAIN][SIM_LOADS] {e}")
                        continue
                    setting = data_parser.parse_simulation_setting(sim_case)
                    value = data_parser.parse_simulation_value(sim_case)
                    idx = data_parser.parse_simulation_receiver(sim_case)
                    sim_case = None
                    gc.collect()
                    bbl_controller.simulation_effect_set(idx, setting, value)
                bbl_controller.simulation_effect_handle()
            except Exception as e:
                bbl_controller.reinit()
                logger.error(f"[MAIN]SIM_TASK: {e}")
                sys.exit()
            await uasyncio.sleep(0.02)

    await uasyncio.gather(
        control_task(),
        period_task(),
        simulation_task(),
        bbl_controller.executor_handle()
    )


class Clock(ulogger.BaseClock):
    def __init__(self):
        self.start = time.time()

    def __call__(self) -> str:
        inv = time.time() - self.start
        return '%d' % (inv)


if __name__ == "__main__":
    from machine import Pin

    rst_c = machine.reset_cause()
    log_clock = Clock()

    log_handler_to_term = ulogger.Handler(
        level=ulogger.INFO,
        colorful=True,
        fmt="&(time)%-&(level)%-&(msg)%",
        clock=log_clock,
        direction=ulogger.TO_TERM,
    )

    log_handler_to_file = ulogger.Handler(
        level=ulogger.INFO,
        fmt="&(time)%-&(level)%-&(msg)%",
        clock=log_clock,
        direction=ulogger.TO_FILE,
        file_name="./log/logging",
        index_file_name="./log/log_index.txt",
        max_file_size=10240
    )

    logger = ulogger.Logger(name=__name__,
                            handlers=(
                                log_handler_to_term,
                                log_handler_to_file))

    rc2str = {
        getattr(machine, i): i
        for i in ('PWRON_RESET',
                  'HARD_RESET',
                  'WDT_RESET',
                  'DEEPSLEEP_RESET',
                  'SOFT_RESET')
    }

    logger.info("[MAIN]{}".format(rc2str.get(rst_c, str(rst_c))))

    # Check the role pin to determine if this is the master or slave instance
    role_pin = Pin(10, Pin.IN)
    if role_pin.value():
        uasyncio.run(master_init())
    else:
        uasyncio.run(slave_init())

# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#

import sys
import machine
import uasyncio
import time
import ulogger

sys.path.append("/app")
if '.frozen' in sys.path:
    sys.path.remove('.frozen')
    sys.path.append('.frozen')


async def master_init():
    import rc_module

    logger = ulogger.Logger()
    logger.info("[MAIN]MASTER_INIT.")

    if rc_module.rc_master_init() is False:
        return

    async def rc_task():
        while True:
            rc_module.file_transfer()
            await uasyncio.sleep(1)

    await uasyncio.gather(rc_task())


conf_update_flag = True


async def slave_init():
    import rc_module
    import gc
    import ujson

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
            update_flag = rc_module.file_transfer()
            if update_flag is True:
                logger.info("[MAIN]CONFIG_UPDATE. ")
                conf_update_flag = True

            await uasyncio.sleep(0.5)

    async def control_task():
        EMPTY_DATA = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        global conf_update_flag
        setting = None
        rc_index = 0

        while True:
            try:
                if conf_update_flag is True:
                    # Free memory before load file.
                    conf_update_flag = False
                    bbl_controller.reinit()
                    rc_conf = None
                    setting = None
                    gc.collect()

                    try:
                        with open('rc_config', 'r') as f:
                            rc_conf = ujson.load(f)
                            gc.collect()
                    except Exception as e:
                        logger.warn(f"[MAIN]CFG_LOAD_ERR:{e}.")
                    gc.collect()

                    rc_index = rc_module.rc_index()
                    data_parser.set_slave_idx(rc_index)
                    if rc_conf is not None:
                        setting = data_parser.parse(rc_conf)
                    del rc_conf
                    gc.collect()

                    logger.info(f"[MAIN]PARSE_UPDATE: {rc_index}")
                    bbl_controller.reinit()

                rc_data = rc_module.rc_slave_data()
                data_parser.set_slave_idx(rc_index)

                if rc_index != rc_module.rc_index():
                    # Must update config
                    conf_update_flag = True
                    continue

                if rc_data and setting and rc_data != EMPTY_DATA:
                    bbl_controller.handler(setting, rc_index, rc_data)
                else:
                    bbl_controller.stop('BEHAVIOR')
            except Exception as e:
                bbl_controller.reinit()
                logger.error(f"[MAIN]CTRL_TASK: {e}")
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

    await uasyncio.gather(control_task(),
                          period_task(),
                          simulation_task(),
                          bbl_controller.executor_handle())


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

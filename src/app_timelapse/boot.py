# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#
# This file is executed on every boot (including wake-boot from deepsleep)

import bbl_product
import ble_module
import shutter_module
import time

_PRODUCT_NAME = "SHUTTER"
_PRODUCT_VERSION = "01.00.00.02"

bbl_product.set_app_name(_PRODUCT_NAME)
bbl_product.set_app_version(_PRODUCT_VERSION)
del bbl_product

shutter_module.shutter_init()
ble_module.ble_shutter_init()
shutter_module.shutter_task_init()

while True:
    print("bbl shutter running")
    time.sleep(1)

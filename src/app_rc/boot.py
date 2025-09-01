# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#
# This file is executed on every boot (including wake-boot from deepsleep)

import bbl_product
import gc

_PRODUCT_NAME = "RC"
_PRODUCT_VERSION = "01.00.00.17"

bbl_product.set_app_name(_PRODUCT_NAME)
bbl_product.set_app_version(_PRODUCT_VERSION)
del bbl_product

gc.collect()

exec(open('./app/rc_main.py').read(), globals())

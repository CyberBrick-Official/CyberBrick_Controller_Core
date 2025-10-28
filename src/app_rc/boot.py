# -*-coding:utf-8-*-
#
# The CyberBrick Codebase License, see the file LICENSE for details.
#
# Copyright (c) 2025 MakerWorld
#
# This file is executed on every boot (including wake-boot from deepsleep)

import bbl_product
import sys

_PRODUCT_NAME = "RC"
_PRODUCT_VERSION = "01.00.00.20"

bbl_product.set_app_name(_PRODUCT_NAME)
bbl_product.set_app_version(_PRODUCT_VERSION)
del bbl_product
del _PRODUCT_NAME
del _PRODUCT_VERSION

sys.path.append('/app')
import rc_main

rc_main.main()

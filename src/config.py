# -*- coding: utf-8 -*-
#
# Global configuration for CyberBrick Controller Core
#

# =========================
# Language / I18N
# =========================
DEFAULT_LANG = "en"          # "en" | "tr"
I18N_LOCALES_PATH = "locales"

# =========================
# Executor
# =========================
EXECUTOR_DEFAULT_TIMEOUT = None   # seconds, None = no timeout
EXECUTOR_LOOP_DELAY = 0.2         # asyncio sleep delay
EXECUTOR_MONITOR_DELAY = 0.1

# =========================
# Safety
# =========================
DANGEROUS_COMMANDS = [
    "exit",
    "quit",
    "sys.exit",
    "os.system",
    "__import__",
    "open",
    "eval",
    "exec",
    "os.",
    "subprocess",
    "os.remove",
    "os.rmdir"
]

# =========================
# Default injected commands
# =========================
DEFAULT_COMMANDS = [
    "import uasyncio as asyncio"
]

# =========================
# Command remap rules
# =========================
REMAP_RULES = {
    "bbl.motors": "control",
    "MotorsController": "MotorsControllerExecMapper",
    "ServosController": "ServosControllerExecMapper"
}

# =========================
# Debug
# =========================
DEBUG = False

# -*- coding: utf-8 -*-
#
# Global configuration file
#

# =========================
# Language / i18n Settings
# =========================

# Default system language
DEFAULT_LANG = "en"

# Supported languages (firmware + UI)
SUPPORTED_LANGUAGES = {
    "en": "English",
    "tr": "Türkçe",
    "ar": "العربية",
    "pl": "Polski",
    "cs": "Čeština",
}

# Locale files path (relative to src/common/i18n.py)
LOCALES_PATH = "../locales"


# =========================
# System / Runtime Settings
# =========================

# Enable debug logs
DEBUG = False

# Garbage collection threshold (optional tuning)
GC_COLLECT_INTERVAL = 2000  # ms


# =========================
# Executor Settings
# =========================

# Default command execution timeout (None = unlimited)
EXECUTOR_TIMEOUT = None


# =========================
# Hardware Defaults
# =========================

# Default motor parameters
MOTOR_DEFAULT_FORWARD = 100
MOTOR_DEFAULT_REVERSE = 100
MOTOR_DEFAULT_OFFSET = 0

# Default LED behavior
LED_DEFAULT_EFFECT = 0      # solid
LED_DEFAULT_DURATION = 1000 # ms
LED_DEFAULT_REPEAT = 1

# Default buzzer / music
BUZZER_DEFAULT_VOLUME = 50


# =========================
# Validation Helpers
# =========================

def is_language_supported(lang: str) -> bool:
    return lang in SUPPORTED_LANGUAGES

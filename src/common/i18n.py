# -*- coding: utf-8 -*-
#
# CyberBrick I18N Module
# JSON-based internationalization loader (MicroPython compatible)
#

import ujson

try:
    import config
    DEFAULT_LANG = getattr(config, "DEFAULT_LANG", "en")
except Exception:
    DEFAULT_LANG = "en"


class I18N:
    def __init__(self, lang=None, locales_path="../locales"):
        self.lang = lang or DEFAULT_LANG
        self.locales_path = locales_path
        self._cache = {}
        self._load_lang(self.lang)

    def _load_lang(self, lang):
        if lang in self._cache:
            return

        try:
            with open("{}/{}.json".format(self.locales_path, lang), "r") as f:
                self._cache[lang] = ujson.load(f)
        except Exception:
            self._cache[lang] = {}

        if lang != "en" and "en" not in self._cache:
            try:
                with open("{}/en.json".format(self.locales_path), "r") as f:
                    self._cache["en"] = ujson.load(f)
            except Exception:
                self._cache["en"] = {}

    def set_lang(self, lang):
        self.lang = lang
        self._load_lang(lang)

    def t(self, key):
        if key in self._cache.get(self.lang, {}):
            return self._cache[self.lang][key]

        if key in self._cache.get("en", {}):
            return self._cache["en"][key]

        return key


# functional shortcut (used by modules)
_i18n = I18N()

def t(key):
    return _i18n.t(key)

# -*- coding: utf-8 -*-

import ujson as json
import os

from config import DEFAULT_LANG, LOCALES_PATH


class I18N:
    def __init__(self, lang=None, locales_path=LOCALES_PATH):
        self.lang = lang or DEFAULT_LANG
        self.locales_path = locales_path

        self._cache = {}
        self._load_lang(self.lang)
        if self.lang != "en":
            self._load_lang("en")

    def set_lang(self, lang):
        if lang != self.lang:
            self.lang = lang
            self._load_lang(lang)

    def _load_lang(self, lang):
        if lang in self._cache:
            return

        path = "{}/{}.json".format(self.locales_path, lang)

        try:
            with open(path, "r") as f:
                self._cache[lang] = json.load(f)
        except Exception:
            self._cache[lang] = {}

    def t(self, key):
        # 1️ selected language
        if key in self._cache.get(self.lang, {}):
            return self._cache[self.lang][key]

        # 2️ english fallback
        if key in self._cache.get("en", {}):
            return self._cache["en"][key]

        # 3️ raw key
        return key


# Global singleton (firmware-friendly)
_i18n = I18N()

def t(key):
    return _i18n.t(key)

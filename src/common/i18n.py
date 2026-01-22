import json

class I18N:
    _instance = None

    def __new__(cls, lang="en"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.lang = lang
            cls._instance.data = {}
            cls._instance.load()
        return cls._instance

    def load(self):
        try:
            with open(f"locales/{self.lang}.json", "r") as f:
                self.data = json.load(f)
        except:
            self.data = {}

    def set_lang(self, lang):
        self.lang = lang
        self.load()

    def t(self, key, **kwargs):
        text = self.data.get(key, key)
        try:
            return text.format(**kwargs)
        except:
            return text

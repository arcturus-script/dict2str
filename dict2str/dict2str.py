from .constants import C, T


class dict2str:
    def __init__(self, content, type=None):
        self.content = content
        self.type = type
        self.func = T.get(self.type, None)

    def set(self, type):
        self.type = type
        self.func = T.get(self.type, None)

    def __str__(self):
        return self.parse()

    def parse(self):
        if self.type is None or self.type not in T:
            return str(self.content)

        res = ""

        for item in self.content:
            for t, v in item.items():
                obj = getattr(C, t)
                res += getattr(obj, self.func)(**v)

        return res

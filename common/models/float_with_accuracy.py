class FloatWithAccuracy:
    def __init__(self, value, accuracy: int = 18):
        self._value = round(value, accuracy)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._value == other._value

    def __hash__(self):
        return hash(self._value)

    def __float__(self):
        return self._value

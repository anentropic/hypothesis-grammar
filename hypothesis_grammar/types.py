import math
from decimal import Decimal
from enum import auto, Enum

from typing_extensions import Final


class Deps(Enum):
    """
    Keys for use with `@inject.params(...)`
    """
    GRAMMAR_PATH = auto()
    GRAMMAR_PARSER = auto()


class Modifiers(str, Enum):
    QUANTIFIED = "~"
    ONE_OR_MORE = "+"
    ZERO_OR_MORE = "*"
    OPTIONAL = "?"


def _validate_numeric(op, other):
    if not isinstance(other, (int, float, Decimal)):
        raise TypeError(
            f"'{op}' not supported between instances of 'int' and '{type(other)}'"
        )


class IntInf(int):
    """
    This only exists so we can pass an unlimited `max_examples` setting
    to hypothesis, it has to pass an `isinstance(intinf, int)` check and basic
    comparison checks.

    For a more comprehensive implementation see:
    https://github.com/NeilGirdhar/extended_int
    (but that one does not pass an isinstance(int) check)
    """
    def __init__(self):
        pass

    def __str__(self):
        return "inf"

    def __repr__(self):
        return "IntInf()"

    def __eq__(self, other):
        _validate_numeric("==", other)
        return other == math.inf

    def __gt__(self, other):
        _validate_numeric(">", other)
        return not other == math.inf

    def __lt__(self, other):
        _validate_numeric("<", other)
        return False

    def __ge__(self, other):
        _validate_numeric(">=", other)
        return True

    def __le__(self, other):
        _validate_numeric("<=", other)
        return other == math.inf


intinf: Final = IntInf()

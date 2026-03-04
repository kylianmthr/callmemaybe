import math
import re


def fn_add_numbers(a: int, b: int) -> int:
    return a + b


def fn_greet(name: str) -> str:
    return f"Hey {name} !"


def fn_reverse_string(s: str) -> str:
    return s[::-1]


def fn_get_square_root(a: int) -> float:
    return math.sqrt(a)


def fn_substitute_string_with_regex(
    source_string: str, regex: str, replacement: str
) -> str:
    matchs = re.findall(regex, source_string)
    if len(matchs) > 0:
        return source_string.replace(matchs[0], replacement)
    return source_string

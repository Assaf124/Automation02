from enum import Enum


class ActionResults(Enum):
    VALID_TIME_DIFFERENCE = 1
    INVALID_TIME_DIFFERENCE = 2
    ERROR = 3

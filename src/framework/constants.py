from enum import Enum


class GenerationStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    EMPTY = "empty"
    TRUNCATED = "truncated"
    FAILED_REASONING_INCOMPLETE = "failed_reasoning_incomplete"

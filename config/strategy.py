from __future__ import annotations

from enum import Enum


class LinkAdaptationStrategy(str, Enum):
    TABLE_LOOKUP = "查表"
    DNN = "DNN"


def normalize_strategy(value: LinkAdaptationStrategy | str) -> LinkAdaptationStrategy:
    if isinstance(value, LinkAdaptationStrategy):
        return value
    try:
        return LinkAdaptationStrategy(value)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported link adaptation strategy: {value}. "
            f"Valid values: {[s.value for s in LinkAdaptationStrategy]}"
        ) from exc

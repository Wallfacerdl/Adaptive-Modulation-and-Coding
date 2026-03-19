from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user_model import User


class OllaPolicy(ABC):
    @abstractmethod
    def optimize(self, user: "User") -> None:
        raise NotImplementedError


@dataclass
class TableLookupOllaConfig:
    bler_target: float
    max_mcs_index: int = 28
    medium_bler_upper: float = 0.03
    low_bler_lower: float = 0.01
    severe_bler_upper: float = 0.30


class TableLookupOllaPolicy(OllaPolicy):
    """Outer-loop adaptation tailored for table lookup baseline."""

    def __init__(self, config: TableLookupOllaConfig) -> None:
        self.config = config

    def optimize(self, user: "User") -> None:
        self._try_increase(user)
        self._try_decrease(user)

    def _try_increase(self, user: "User") -> None:
        while user.bler < self.config.bler_target and user.mcs_index < self.config.max_mcs_index:
            if user.bler > self.config.medium_bler_upper:
                break
            user.transmission_time += 1

            if user.bler < self.config.low_bler_lower:
                user.apply_mcs_index(self.config.max_mcs_index)
                break

            if user.mcs_index == self.config.max_mcs_index - 1:
                delta = 1
            elif user.mcs_index == self.config.max_mcs_index - 2:
                delta = 2
            else:
                delta = 3
            user.apply_mcs_index(user.mcs_index + delta)

    def _try_decrease(self, user: "User") -> None:
        while user.bler > self.config.bler_target and user.mcs_index > 1:
            user.transmission_time += 1
            if user.bler > self.config.severe_bler_upper:
                user.apply_mcs_index(user.mcs_index - 3)
            else:
                user.apply_mcs_index(user.mcs_index - 2)


class DNNOllaPolicy(OllaPolicy):
    """Conservative fallback for DNN outputs."""

    def __init__(self, bler_target: float, soft_cap: float = 0.2) -> None:
        self.bler_target = bler_target
        self.soft_cap = soft_cap

    def optimize(self, user: "User") -> None:
        if user.bler <= self.bler_target:
            return
        if user.bler >= self.soft_cap and user.mcs_index > 0:
            user.transmission_time += 1
            user.apply_mcs_index(user.mcs_index - 1)

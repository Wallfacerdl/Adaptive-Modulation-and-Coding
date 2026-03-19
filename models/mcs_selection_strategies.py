from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from DL.train_wrapper import AIMSController
from config.DefaultConfig import CONFIG
from config.paths import DL_RESULTS_ROOT
from utils.get_mcs_index import get_initial_mcs_index

if TYPE_CHECKING:
    from models.user_model import User


class MCSSelectionStrategy(ABC):
    """Select an MCS index before outer-loop optimization."""

    @abstractmethod
    def select_index(self, user: "User") -> int:
        raise NotImplementedError


class TableLookupSelectionStrategy(MCSSelectionStrategy):
    def select_index(self, user: "User") -> int:
        return get_initial_mcs_index(user.cqi)


class DNNSelectionStrategy(MCSSelectionStrategy):
    def __init__(self) -> None:
        pth_name = (
            f"{CONFIG.ai.pth_time}_{CONFIG.ai.model_name[:-4]}_{CONFIG.ai.data_mode}.pth"
        )
        self.controller = AIMSController(str(DL_RESULTS_ROOT / pth_name))

    def select_index(self, user: "User") -> int:
        return self.controller.safe_select_mcs(user.snr)

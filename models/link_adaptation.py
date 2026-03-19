# models/link_adaptation.py
from utils.mapping import mcs_index_map
from config.strategy import LinkAdaptationStrategy, normalize_strategy
from models.mcs_selection_strategies import (
    DNNSelectionStrategy,
    MCSSelectionStrategy,
    TableLookupSelectionStrategy,
)

class LinkAdaptation:
    def __init__(self, strategy):
        self.strategy = normalize_strategy(strategy)
        self._selection_strategy = self._build_selection_strategy(self.strategy)

    @staticmethod
    def _build_selection_strategy(strategy: LinkAdaptationStrategy) -> MCSSelectionStrategy:
        if strategy == LinkAdaptationStrategy.TABLE_LOOKUP:
            return TableLookupSelectionStrategy()
        if strategy == LinkAdaptationStrategy.DNN:
            return DNNSelectionStrategy()
        raise ValueError("无效的策略")

    def select_mcs(self, user):
        index = self._selection_strategy.select_index(user)
        return self.select_mcs_by_index(index)

    def select_mcs_by_index(self, mcs_index: int):
        return mcs_index_map[mcs_index]

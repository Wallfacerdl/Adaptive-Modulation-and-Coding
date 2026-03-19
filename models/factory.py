from __future__ import annotations

from config.strategy import LinkAdaptationStrategy, normalize_strategy
from models.link_adaptation import LinkAdaptation
from models.olla_policy import (
    DNNOllaPolicy,
    OllaPolicy,
    TableLookupOllaConfig,
    TableLookupOllaPolicy,
)


class LinkAdaptationFactory:
    _adaptation_cache: dict[str, LinkAdaptation] = {}

    @classmethod
    def get_link_adaptation(cls, strategy: str) -> LinkAdaptation:
        strategy_enum = normalize_strategy(strategy)
        cache_key = strategy_enum.value
        if cache_key not in cls._adaptation_cache:
            cls._adaptation_cache[cache_key] = LinkAdaptation(strategy=strategy_enum)
        return cls._adaptation_cache[cache_key]

    @staticmethod
    def create_olla_policy(
        strategy: str,
        bler_target: float,
        max_mcs_index: int,
        olla_config: dict | None = None,
    ) -> OllaPolicy:
        strategy_enum = normalize_strategy(strategy)
        olla_config = olla_config or {}
        if strategy_enum == LinkAdaptationStrategy.TABLE_LOOKUP:
            table_cfg = olla_config.get("table", {})
            return TableLookupOllaPolicy(
                TableLookupOllaConfig(
                    bler_target=bler_target,
                    max_mcs_index=max_mcs_index,
                    medium_bler_upper=table_cfg.get("medium_bler_upper", 0.03),
                    low_bler_lower=table_cfg.get("low_bler_lower", 0.01),
                    severe_bler_upper=table_cfg.get("severe_bler_upper", 0.30),
                )
            )
        if strategy_enum == LinkAdaptationStrategy.DNN:
            dnn_cfg = olla_config.get("dnn", {})
            return DNNOllaPolicy(
                bler_target=bler_target,
                soft_cap=dnn_cfg.get("soft_cap", 0.2),
            )
        raise ValueError(f"Unsupported link adaptation strategy: {strategy_enum}")

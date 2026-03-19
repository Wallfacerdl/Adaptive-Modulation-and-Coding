from __future__ import annotations

from config.strategy import normalize_strategy


def validate_config(config) -> None:
    """Validate critical runtime settings before simulation starts."""
    config.link_adaptation.strategy = normalize_strategy(config.link_adaptation.strategy)

    if config.simulation.num_users <= 0:
        raise ValueError("simulation.num_users must be positive")
    if config.simulation.tti_length <= 0:
        raise ValueError("simulation.tti_length must be positive")
    if config.link_adaptation.bler_target <= 0 or config.link_adaptation.bler_target >= 1:
        raise ValueError("link_adaptation.bler_target must be in (0, 1)")

    table = config.link_adaptation.olla.get("table", {})
    dnn = config.link_adaptation.olla.get("dnn", {})

    for key in ["medium_bler_upper", "low_bler_lower", "severe_bler_upper"]:
        val = table.get(key)
        if val is None or val <= 0 or val >= 1:
            raise ValueError(f"link_adaptation.olla.table.{key} must be in (0, 1)")

    if table["low_bler_lower"] >= table["medium_bler_upper"]:
        raise ValueError("link_adaptation.olla.table.low_bler_lower must be less than medium_bler_upper")

    soft_cap = dnn.get("soft_cap")
    if soft_cap is None or soft_cap <= 0 or soft_cap >= 1:
        raise ValueError("link_adaptation.olla.dnn.soft_cap must be in (0, 1)")

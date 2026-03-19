from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.DefaultConfig import CONFIG
from config.config_validator import validate_config
from config.paths import RESULTS_ROOT
from config.strategy import LinkAdaptationStrategy
from config.update_config import update_config
from simulations.facade import SimulationFacade


CASES = [
    {
        "name": "baseline",
        "table": {
            "medium_bler_upper": 0.03,
            "low_bler_lower": 0.01,
            "severe_bler_upper": 0.30,
        },
        "dnn": {"soft_cap": 0.20},
    },
    {
        "name": "aggressive_up",
        "table": {
            "medium_bler_upper": 0.04,
            "low_bler_lower": 0.015,
            "severe_bler_upper": 0.30,
        },
        "dnn": {"soft_cap": 0.22},
    },
    {
        "name": "conservative_down",
        "table": {
            "medium_bler_upper": 0.025,
            "low_bler_lower": 0.008,
            "severe_bler_upper": 0.25,
        },
        "dnn": {"soft_cap": 0.18},
    },
]


def _snapshot_runtime_config() -> dict:
    return {
        "strategy": CONFIG.link_adaptation.strategy,
        "bler_target": CONFIG.link_adaptation.bler_target,
        "olla": json.loads(json.dumps(CONFIG.link_adaptation.olla)),
        "num_users": CONFIG.simulation.num_users,
        "tti_length": CONFIG.simulation.tti_length,
        "save_info": CONFIG.simulation.save_info,
        "save_training_results": CONFIG.simulation.save_training_results,
        "show": {
            "plot_hist_snr": CONFIG.show.plot_hist_snr,
            "plot_throughput_distribution": CONFIG.show.plot_throughput_distribution,
            "plot_cqi_distribution": CONFIG.show.plot_cqi_distribution,
            "show_bler_analysis": CONFIG.show.show_bler_analysis,
            "print_summary_stats": CONFIG.show.print_summary_stats,
            "plot_mcs_distribution": CONFIG.show.plot_mcs_distribution,
            "show_snr_mcsindex": CONFIG.show.show_snr_mcsindex,
            "show_delay_distribution": CONFIG.show.show_delay_distribution,
            "show_user_HistoryData": CONFIG.show.show_user_HistoryData,
            "show_snr_bijiao": CONFIG.show.show_snr_bijiao,
        },
    }


def _restore_runtime_config(snapshot: dict) -> None:
    update_config(
        CONFIG,
        link_adaptation__strategy=snapshot["strategy"],
        link_adaptation__bler_target=snapshot["bler_target"],
        link_adaptation__olla=snapshot["olla"],
        simulation__num_users=snapshot["num_users"],
        simulation__tti_length=snapshot["tti_length"],
        simulation__save_info=snapshot["save_info"],
        simulation__save_training_results=snapshot["save_training_results"],
        show__plot_hist_snr=snapshot["show"]["plot_hist_snr"],
        show__plot_throughput_distribution=snapshot["show"]["plot_throughput_distribution"],
        show__plot_cqi_distribution=snapshot["show"]["plot_cqi_distribution"],
        show__show_bler_analysis=snapshot["show"]["show_bler_analysis"],
        show__print_summary_stats=snapshot["show"]["print_summary_stats"],
        show__plot_mcs_distribution=snapshot["show"]["plot_mcs_distribution"],
        show__show_snr_mcsindex=snapshot["show"]["show_snr_mcsindex"],
        show__show_delay_distribution=snapshot["show"]["show_delay_distribution"],
        show__show_user_HistoryData=snapshot["show"]["show_user_HistoryData"],
        show__show_snr_bijiao=snapshot["show"]["show_snr_bijiao"],
    )


def _run_one_case(case: dict, num_users: int, tti_length: int) -> dict:
    update_config(
        CONFIG,
        link_adaptation__strategy=LinkAdaptationStrategy.TABLE_LOOKUP,
        link_adaptation__bler_target=0.1,
        link_adaptation__olla={"table": case["table"], "dnn": case["dnn"]},
        simulation__num_users=num_users,
        simulation__tti_length=tti_length,
        simulation__save_info=False,
        simulation__save_training_results=False,
        show__plot_hist_snr=False,
        show__plot_throughput_distribution=False,
        show__plot_cqi_distribution=False,
        show__show_bler_analysis=False,
        show__print_summary_stats=False,
        show__plot_mcs_distribution=False,
        show__show_snr_mcsindex=False,
        show__show_delay_distribution=False,
        show__show_user_HistoryData=False,
        show__show_snr_bijiao=False,
    )
    validate_config(CONFIG)

    results = SimulationFacade().run()

    avg_bler_all = sum(results.bler_values) / len(results.bler_values)
    throughput_ratio = results.total_throughput / results.theoretical_throughput
    avg_time_throughput = results.total_time_throughput / CONFIG.simulation.tti_length
    time_ratio = avg_time_throughput / results.theoretical_throughput

    return {
        "case": case["name"],
        "num_users": CONFIG.simulation.num_users,
        "tti_length": CONFIG.simulation.tti_length,
        "avg_bler": avg_bler_all,
        "avg_delay_ms": results.avg_delay * 1e3,
        "instant_throughput_gbps": results.total_throughput / 1e9,
        "instant_ratio": throughput_ratio,
        "time_avg_throughput_gbps": avg_time_throughput / 1e9,
        "time_avg_ratio": time_ratio,
    }


def _persist_rows(rows: list[dict], sweep_dir: Path) -> None:
    sweep_dir.mkdir(parents=True, exist_ok=True)
    csv_path = sweep_dir / "summary.csv"
    json_path = sweep_dir / "summary.json"

    with csv_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with json_path.open("w", encoding="utf-8") as fp:
        json.dump(rows, fp, ensure_ascii=False, indent=2)


def main() -> None:
    snapshot = _snapshot_runtime_config()
    timestamp = datetime.now().strftime("%Y%m%d_%H-%M-%S")
    sweep_dir = RESULTS_ROOT / f"olla_sweep_{timestamp}"
    rows: list[dict] = []

    try:
        for case in CASES:
            row = _run_one_case(case=case, num_users=300, tti_length=60)
            rows.append(row)
            print(
                f"[{row['case']}] BLER={row['avg_bler']:.4f}, "
                f"Delay={row['avg_delay_ms']:.3f}ms, "
                f"TimeRatio={row['time_avg_ratio']:.2%}"
            )

        _persist_rows(rows, sweep_dir)
        print(f"Sweep completed. Results saved to: {sweep_dir}")
    finally:
        _restore_runtime_config(snapshot)


if __name__ == "__main__":
    main()

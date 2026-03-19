from __future__ import annotations

from models.gNB_model import BaseStation
from simulations.results import SimulationResults


class SimulationFacade:
    """Facade for end-to-end simulation orchestration."""

    def run(self) -> SimulationResults:
        base_station = BaseStation()
        base_station.update_users()

        results = SimulationResults()
        results.collect_calculate_data(base_station, base_station.users)
        results.show_all_results()
        results.save_data_for_training()
        return results

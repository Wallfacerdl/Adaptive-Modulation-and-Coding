from models.gNB_model import BaseStation
from simulations.results import SimulationResults


def run_simulation():

    # 初始化基站
    base_station = BaseStation()

    # 运行仿真
    base_station.update_users()

    # 收集仿真结果并展示
    results = SimulationResults()
    results.collect_calculate_data(base_station, base_station.users)  # 收集用户数据
    results.show_all_results()  # 展示吞吐量、CQI、MCS 等结果
    results.save_results()  # 保存结果

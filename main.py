"""
•	职责：这个文件是整个仿真系统的入口，负责初始化配置、运行仿真、输出结果等。
•	内容：
•	导入其他模块并调用仿真方法。
•	解析配置文件（例如：读取用户数量、带宽、信道类型等）。
•	调用仿真函数，获取性能评估结果。
"""

## 参数预设置
from simulations.simulation import run_simulation
from config.update_config import update_config
from config.DefaultConfig import CONFIG


def main():
    """
    加载所有配置并运行仿真
    :return:
    """
    # 修改部分默认配置
    update_config(
        CONFIG,
        simulation__num_users=100,
        phy_layer_bandwidth=10e9,  # 大于180MHZ
        simulation__save_training_results=True,
        simulation__tti_length=100,
        link_adaptation__strategy="查表",  # 或者'DNN'
    )
    run_simulation()


if __name__ == "__main__":
    main()

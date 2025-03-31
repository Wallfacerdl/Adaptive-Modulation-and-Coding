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
from utils.generate_save_path import generate_save_path


def main():
    """
    加载所有配置并运行仿真
    :return:
    """
    # 将工作目录设置为项目根目录
    import os

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # print(os.getcwd())

    # 修改部分常用的默认配置
    update_config(
        CONFIG,
        phy_layer_bandwidth = 10e9,  # 大于180MHZ
        simulation__num_users=100000000,  # 用户数
        simulation__save_info=True,
        simulation__save_training_results=True,
        simulation__tti_length=1, # slot个数
        link_adaptation__strategy="查表",  # 或者'DNN'（加载DNN模型时即为模型的验证）
        channel__ar_model={"alpha": 0.9, "sigma_ar": 0.1},  # 更改信道模型参数
        ai__data_mode = 'Complex', # Complex或Lite 若为查表模式则表示数据集的大小；若为DNN模式则表示搭载模型是否轻量化
    )

    # 如果需要保存文件的话，则创建文件夹
    if CONFIG.simulation.save_info:
        update_config(CONFIG, simulation__save_path=generate_save_path())
    if CONFIG.link_adaptation.strategy == "DNN":
        update_config(
            CONFIG,
            ai__pth_time = "20250330_01-22" # 选择搭载的模型训练时间戳
            )
    print("Simulation begins…")

    run_simulation()


if __name__ == "__main__":
    main()

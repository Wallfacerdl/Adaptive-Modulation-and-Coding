# models/base_station_model.py
from models.user_model import User  # 导入User类
from models.channel_model import InitSNRGenerator
from config.DefaultConfig import CONFIG


# 调用预配置


class BaseStation:
    def __init__(self):
        self.total_throughput = 0  # 初始化吞吐量
        # 初始化用户
        # 考虑阴影衰落，生成正态分布的SNR(dB)
        init_snr_sequences = InitSNRGenerator(CONFIG.simulation.num_users,
                                              CONFIG.channel.snr['medium'],
                                              CONFIG.channel.snr['sigma'],
                                              CONFIG.channel.snr['init_range'][0],
                                              CONFIG.channel.snr['init_range'][1]).generate()
        snr_list = init_snr_sequences["values"]
        self.new_mean_snr = init_snr_sequences["new_median"]
        # print(init_snr_sequences["new_median"])

        self.users = [User(user_id, snr) for user_id, snr in enumerate(snr_list)]

    def update_users(self):
        """在基站中随时间动态更新所有用户的CQI、MCS以及信道"""
        update_num = 0
        """时间维度loop"""
        for _ in range(CONFIG.simulation.tti_length):
            for user in self.users:
                user.update_link()  ## user的更新函数只通过update_link()函数实现而屏蔽了其他——体现了抽象的思想
                if user.update:
                    update_num += 1
        # print(f"更新过的用户数：{update_num}")

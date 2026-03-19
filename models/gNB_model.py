# models/base_station_model.py
from models.user_model import User  # 导入User类
from models.channel_model import InitSNRGenerator
from models.factory import LinkAdaptationFactory
from config.DefaultConfig import CONFIG
from utils.mapping import mcs_index_map


# 调用预配置


class BaseStation:
    def __init__(self):
        self.total_throughput = 0  # 初始化吞吐量
        strategy = CONFIG.link_adaptation.strategy
        self.link_adaptation = LinkAdaptationFactory.get_link_adaptation(strategy)
        self.olla_policy = LinkAdaptationFactory.create_olla_policy(
            strategy=strategy,
            bler_target=CONFIG.link_adaptation.bler_target,
            max_mcs_index=max(mcs_index_map.keys()),
            olla_config=CONFIG.link_adaptation.olla,
        )
        # 初始化用户
        # 考虑阴影衰落，生成正态分布的SNR(dB)
        init_snr_sequences = InitSNRGenerator(
            CONFIG.simulation.num_users,
            CONFIG.channel.snr["medium"],
            CONFIG.channel.snr["sigma"],
            CONFIG.channel.snr["init_range"][0],
            CONFIG.channel.snr["init_range"][1],
        ).generate()
        self.origin_snr_list = init_snr_sequences["origin_snr_list"]
        self.snr_list = init_snr_sequences["cur_values"]
        self.new_mean_snr = init_snr_sequences["new_median"]
        self.users = [
            User(
                user_id=user_id,
                snr=snr,
                link_adaptation=self.link_adaptation,
                olla_policy=self.olla_policy,
            )
            for user_id, snr in enumerate(self.snr_list)
        ]

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

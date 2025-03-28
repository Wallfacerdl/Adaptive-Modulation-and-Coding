# models/user_model.py

# 导入函数
from utils.snr_to_cqi import snr_to_cqi
from utils.bler_estimation import estimate_bler  # 新增导入
from utils.mapping import mcs_index_map
from models.link_adaptation import LinkAdaptation
from models.channel_model import AR_SNR_Generator
from config.DefaultConfig import CONFIG


class User:
    def __init__(self, user_id: int, snr: float):
        # 基础信息
        self.user_id = user_id
        self.snr = snr
        self.la = LinkAdaptation(
            strategy = CONFIG.link_adaptation.strategy
            )  # 使用链路自适应
        self.update = False
        # passlossModel_撒点模型
        # 初始化CQI和MCS
        self.cqi = snr_to_cqi(self.snr)
        self.mcs = self.la.select_mcs(self)
        self.mcs_index = self.mcs["index"]
        self.bler = estimate_bler(self.snr, self.cqi, self.mcs)  # 新增BLER

        # 时间维度信息
        self.snr_history = [snr]  # 记录SNR历史
        self.cqi_history = [self.cqi]  # 记录CQI历史
        self.mcs_history = [self.mcs_index]  # 记录MCS历史
        self.bler_history = [self.bler]  # 记录BLER历史
        # 性能指标
        self.throughput = 0
        self.transmission_time = 0  # 累积总传输次数
        self.snr_generator = AR_SNR_Generator(
            init_snr_db = self.snr,
            sigma_db = CONFIG.channel.snr["sigma"],
            alpha = CONFIG.channel.ar_model["alpha"],
            )  # 信道模型

    def update_link(self):
        """统一更新信道、CQI 和 MCS"""
        self.__update_channel()
        self.transmission_time += 1
        # TODO:更新信道后需要更新SNR后再更新CQI和MCS
        self.__update_snr()
        self.__update_cqi()
        self.__update_mcs()
        self.__update_bler()  # 新增BLER计算
        """外环链路自适应"""
        while (
                self.bler < CONFIG.link_adaptation.bler_target
                and self.mcs_index < 28
                and CONFIG.link_adaptation.strategy == "查表"
        ):
            # 达标
            # print('初始MCS:', self.mcs)
            self.transmission_time += 1
            self.update = True
            if self.mcs_index == 27:
                self.mcs_index += 1
            elif self.mcs_index == 26:
                self.mcs_index += 2
            else:
                self.mcs_index += 3
            self.__update_mcs(synchronous = True)
            self.__update_bler(synchronous = True)
        while (
                self.bler > CONFIG.link_adaptation.bler_target
                and self.mcs_index > 1
                and CONFIG.link_adaptation.strategy == "查表"
        ):
            # 不达标
            # print('初始MCS:', self.mcs)
            self.transmission_time += 1
            self.update = True
            self.mcs_index -= 1
            self.__update_mcs(synchronous = True)
            self.__update_bler(synchronous = True)  # 新增BLER计算
            # print('更新MCS:', self.mcs)

    def __update_channel(self):
        pass

    def __update_snr(self):
        """更新SNR"""
        self.snr = self.snr_generator.next_snr()
        self.snr_history.append(self.snr)

    def __update_cqi(self):
        """根据SNR更新CQI"""
        self.cqi = snr_to_cqi(self.snr)
        self.cqi_history.append(self.cqi)

    def __update_mcs(self, synchronous = False):
        """通过LinkAdaptation选择MCS"""
        self.mcs = self.la.select_mcs(self)
        self.mcs_index = self.mcs["index"]
        if synchronous:
            self.mcs_history[-1] = self.mcs_index
        else:
            self.mcs_history.append(self.mcs_index)

    def plot(self):
        import matplotlib.pyplot as plt
        from utils.font_setting import font_setting

        font_setting()
        """绘制用户的时间维度信息"""
        fig, axs = plt.subplots(2, 2, figsize = (12, 8))

        # Plot SNR history
        axs[0, 0].plot(self.snr_history, label = "SNR (dB)")
        axs[0, 0].set_title("SNR History")
        axs[0, 0].set_xlabel("Time")
        axs[0, 0].set_ylabel("SNR (dB)")
        axs[0, 0].legend()

        # Plot CQI history
        axs[0, 1].plot(self.cqi_history, label = "CQI", color = "orange")
        axs[0, 1].set_title("CQI History")
        axs[0, 1].set_xlabel("Time")
        axs[0, 1].set_ylabel("CQI")
        axs[0, 1].legend()

        # Plot MCS history
        axs[1, 0].plot(self.mcs_history, label = "MCS Index", color = "green")
        axs[1, 0].set_title("MCS History")
        axs[1, 0].set_xlabel("Time")
        axs[1, 0].set_ylabel("MCS Index")
        axs[1, 0].legend()

        # Plot BLER history
        axs[1, 1].plot(self.bler_history, label = "BLER", color = "red")
        axs[1, 1].set_title("BLER History")
        axs[1, 1].set_xlabel("Time")
        axs[1, 1].set_ylabel("BLER")
        axs[1, 1].legend()

        plt.tight_layout()
        if CONFIG.simulation.save_info:
            import os
            plt.savefig(,format = 'svg', dpi=300)
        # # 保存
        # if CONFIG.show.show_user_HistoryData:
        #     plt.savefig(f"../results/user_{self.user_id}.png")
        plt.show()

    def __update_bler(self, synchronous = False):
        """计算当前BLER"""
        self.bler = estimate_bler(self.snr, self.cqi, self.mcs)
        if synchronous:
            self.bler_history[-1] = self.bler
        else:
            self.bler_history.append(self.bler)

    def calculate_throughput(self, total_bandwidth, cur_time = -1) -> None:
        """根据MCS计算某一时刻的吞吐量"""
        # 1.计算资源块数（向上取整）
        from math import ceil

        num_rbs = ceil(
            total_bandwidth / CONFIG.phy_layer.rb_bandwidth
            )  # 总带宽带宽下的资源块数

        # 2.获取当前时刻的MCS和BLER
        cur_mcs = mcs_index_map[self.mcs_history[cur_time]]
        cur_bler = self.bler_history[cur_time]
        mcs, cur_efficiency = cur_mcs["modulation"], cur_mcs["efficiency"]

        # 3.计算有效频谱效率
        effected_efficiency = cur_efficiency * (1 - cur_bler)

        # 4.用户资源分配（假设均分RB）
        rbs_per_user = num_rbs // CONFIG.simulation.num_users  # 整数分配，余数需处理
        if rbs_per_user == 0:
            rbs_per_user = 1
        allocated_bandwidth = CONFIG.phy_layer.rb_bandwidth * rbs_per_user
        # users_per_rb = CONFIG.simulation.num_users / num_rbs
        # allocated_bandwidth = CONFIG.phy_layer.rb_bandwidth / users_per_rb
        if cur_time == -1:
            self.throughput = allocated_bandwidth * effected_efficiency
        else:
            return allocated_bandwidth * effected_efficiency

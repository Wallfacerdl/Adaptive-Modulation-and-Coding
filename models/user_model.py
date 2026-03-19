# models/user_model.py

# 导入函数
from utils.snr_to_cqi import snr_to_cqi
from utils.bler_estimation import estimate_bler  # 新增导入
from utils.mapping import mcs_index_map
from models.link_adaptation import LinkAdaptation
from models.link_update_template import LinkUpdateTemplate
from models.olla_policy import OllaPolicy
from models.channel_model import AR_SNR_Generator
from config.DefaultConfig import CONFIG


class User(LinkUpdateTemplate):
    def __init__(
        self,
        user_id: int,
        snr: float,
        link_adaptation: LinkAdaptation | None = None,
        olla_policy: OllaPolicy | None = None,
    ):
        # 基础信息
        self.user_id = user_id
        self.snr = snr
        self.la = link_adaptation or LinkAdaptation(
            strategy=CONFIG.link_adaptation.strategy
        )
        self.max_mcs_index = max(mcs_index_map.keys())
        self.update = False

        if olla_policy is None:
            from models.factory import LinkAdaptationFactory

            self.olla_policy = LinkAdaptationFactory.create_olla_policy(
                strategy=CONFIG.link_adaptation.strategy,
                bler_target=CONFIG.link_adaptation.bler_target,
                max_mcs_index=self.max_mcs_index,
                olla_config=CONFIG.link_adaptation.olla,
            )
        else:
            self.olla_policy = olla_policy

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
            init_snr_db=self.snr,
            sigma_db=CONFIG.channel.snr["sigma"],
            alpha=CONFIG.channel.ar_model["alpha"],
        )  # 信道模型

    def _before_update(self):
        self.update = False

    def _update_channel(self):
        pass

    def _mark_transmission(self):
        self.transmission_time += 1

    def _update_snr(self):
        """更新SNR"""
        self.snr = self.snr_generator.next_snr()
        self.snr_history.append(self.snr)

    def _update_cqi(self):
        """根据SNR更新CQI"""
        self.cqi = snr_to_cqi(self.snr)
        self.cqi_history.append(self.cqi)

    def _update_mcs(self):
        """通过LinkAdaptation选择初始MCS"""
        self.mcs = self.la.select_mcs(self)
        self.mcs_index = self.mcs["index"]
        self.mcs_history.append(self.mcs_index)

    def _update_bler(self):
        """计算当前BLER"""
        self.bler = estimate_bler(self.snr, self.cqi, self.mcs)
        self.bler_history.append(self.bler)

    def _optimize_outer_loop(self):
        self.olla_policy.optimize(self)

    def apply_mcs_index(self, new_index: int) -> bool:
        """Apply an MCS index during outer-loop optimization."""
        bounded = max(0, min(new_index, self.max_mcs_index))
        changed = bounded != self.mcs_index

        self.mcs_index = bounded
        self.mcs = self.la.select_mcs_by_index(self.mcs_index)
        self.bler = estimate_bler(self.snr, self.cqi, self.mcs)

        self.mcs_history[-1] = self.mcs_index
        self.bler_history[-1] = self.bler

        if changed:
            self.update = True
        return changed

    def plot(self):
        import matplotlib.pyplot as plt
        from utils.font_setting import font_setting

        font_setting()
        """绘制用户的时间维度信息"""
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))

        # Plot SNR history
        axs[0, 0].plot(self.snr_history, label="SNR (dB)")
        axs[0, 0].set_title("SNR History")
        axs[0, 0].set_xlabel("Time")
        axs[0, 0].set_ylabel("SNR (dB)")
        axs[0, 0].legend()

        # Plot CQI history
        axs[0, 1].plot(self.cqi_history, label="CQI", color="orange")
        axs[0, 1].set_title("CQI History")
        axs[0, 1].set_xlabel("Time")
        axs[0, 1].set_ylabel("CQI")
        axs[0, 1].legend()

        # Plot MCS history
        axs[1, 0].plot(self.mcs_history, label="MCS Index", color="green")
        axs[1, 0].set_title("MCS History")
        axs[1, 0].set_xlabel("Time")
        axs[1, 0].set_ylabel("MCS Index")
        axs[1, 0].legend()

        # Plot BLER history
        axs[1, 1].plot(self.bler_history, label="BLER", color="red")
        axs[1, 1].set_title("BLER History")
        axs[1, 1].set_xlabel("Time")
        axs[1, 1].set_ylabel("BLER")
        axs[1, 1].legend()

        plt.tight_layout()
        if CONFIG.simulation.save_info:
            import os

            plt.savefig(
                CONFIG.simulation.save_path + f"//user_{self.user_id}_data.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def calculate_throughput(self, total_bandwidth, cur_time=-1) -> None:
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

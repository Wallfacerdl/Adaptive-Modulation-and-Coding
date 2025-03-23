"""
吞吐量的计算
"""
from config.DefaultConfig import CONFIG
import numpy as np


class ThroughputCalculator:
    def __init__(self, base_station):
        self.base_station = base_station
        self.total_throughput = 0
        self.theoretical_throughput = 0
        self.total_time_throughput = 0

    def calculate_total_throughput(self):
        """计算当前时刻所有用户的总吞吐量"""
        for user in self.base_station.users:
            # 测试bler固定为0时候的效果
            user.calculate_throughput(CONFIG.phy_layer.bandwidth, cur_time = -1)
            self.total_throughput += user.throughput
        return self.total_throughput

    def calculate_TotalTime_throughput(self):
        """计算总时间上所有用户的总吞吐量"""
        for time in range(CONFIG.simulation.tti_length):
            for user in self.base_station.users:
                # 测试bler固定为0时候的效果
                throughput = user.calculate_throughput(CONFIG.phy_layer.bandwidth, time)
                self.total_time_throughput += throughput
        return self.total_time_throughput

    def calculate_theoretical_throughput(self):
        """计算理论吞吐量"""
        # C = B*log2(1 + SNR)
        B = CONFIG.phy_layer.bandwidth
        snr_medium = self.base_station.new_mean_snr
        snr_linear = 10 ** (snr_medium / 10)  # 将SNR从dB转换为线性值
        self.theoretical_throughput = B * np.log2(1 + snr_linear)
        return self.theoretical_throughput

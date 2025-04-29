# utils/results.py
import matplotlib.pyplot as plt
from metrics.throughput import ThroughputCalculator
from metrics.delay import DelayCalculator
from metrics.bler import BLERCalculator
import numpy as np
from config.DefaultConfig import CONFIG
from utils.font_setting import font_setting
import os
from datetime import datetime

font_setting()


class SimulationResults:
    def __init__(self):
        self.total_throughput = 0
        self.total_time_throughput = 0
        self.theoretical_throughput = 0
        self.avg_delay = 0
        self.avg_bler = 0
        self.throughputs = []
        self.cqi_values = []
        self.mcs_order = []
        self.user_ids = []
        self.mcs_de_duplicative = []
        self.bler_values = []
        self.final_snr_list = []
        self.modulation = []
        self.cqi_bler = {}
        self.transmission_time = []
        self.mcs_index = []
        self.efficiency = []
        self.save_path = CONFIG.simulation.save_path
        self.origin_snr_list = []
        self.user0_history_data = []

    def collect_calculate_data(self, base_station, users):
        """收集用户的吞吐量、CQI、MCS 数据"""
        ## 基站数据
        throughputCalculator = ThroughputCalculator(base_station)
        self.total_throughput = throughputCalculator.calculate_total_throughput()
        self.total_time_throughput = (
            throughputCalculator.calculate_TotalTime_throughput()
        )
        self.theoretical_throughput = (
            throughputCalculator.calculate_theoretical_throughput()
        )

        # self.snr_values = base_station.snr_list
        self.origin_snr_list = base_station.origin_snr_list
        for user in users:
            if user.user_id <10:
                user.plot()
            self.final_snr_list.append(user.snr)
            self.user_ids.append(user.user_id)
            self.throughputs.append(user.throughput)
            self.cqi_values.append(user.cqi)
            self.mcs_order.append(user.mcs["order"])  # 取调制阶数，例如 2, 4, 16, 64
            self.efficiency.append(
                user.mcs["efficiency"]
            )  # 取调制阶数，例如 2, 4, 16, 64
            self.bler_values.append(user.bler)  # 误块率
            self.modulation.append(
                user.mcs["modulation"]
            )  # 取调制方式，例如 QPSK, 16QAM, 64QAM
            # 平均单个TTI的传输次数
            self.transmission_time.append(
                user.transmission_time / CONFIG.simulation.tti_length
            )
            if user.mcs["modulation"] not in self.mcs_de_duplicative:
                self.mcs_de_duplicative.append(user.mcs["modulation"])
            self.cqi_bler.setdefault(user.cqi, []).append(user.bler)
            self.mcs_index.append(user.mcs_index)
        self.avg_bler = BLERCalculator(
            self.modulation, self.bler_values
        ).calculate_avg_bler()
        self.avg_delay = DelayCalculator(
            self.transmission_time
        ).calculate_average_delay()

    def cut_snr_bijiao(self):
        """对比原始SNR和最终SNR"""
        plt.subplot(1, 2, 1)
        # bins参数是指定bin(箱子)的个数，也就是总共有几条条状图
        plt.hist(self.origin_snr_list, bins=13, edgecolor="black", alpha=0.7)
        plt.suptitle("SNR Distribution")
        plt.title("截断前")
        plt.subplot(1, 2, 2)
        plt.hist(self.final_snr_list, bins=13, edgecolor="black", alpha=0.7)
        plt.title("截断后")
        if CONFIG.simulation.save_info:
            plt.savefig(
                self.save_path + "//" + "SNR截断前后对比.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def plot_throughput_distribution(self):
        """绘制吞吐量分布图"""
        plt.figure(figsize=(8, 5))
        plt.bar(
            self.user_ids, np.array(self.throughputs) / (10**6), color="blue", alpha=0.7
        )
        plt.xlabel("用户 ID")
        plt.ylabel("吞吐量 (Mbps)")
        plt.title("用户吞吐量分布")
        plt.grid()
        if CONFIG.simulation.save_info:
            plt.savefig(
                self.save_path + "//" + "throughput distribution.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def plot_cqi_distribution(self):
        """绘制 CQI 分布情况"""
        plt.figure(figsize=(8, 5))
        plt.hist(
            self.cqi_values, bins=np.arange(1, 16) - 0.5, edgecolor="black", alpha=0.7
        )
        # Bins是直方图的柱子的个数，bins=10表示将数据分成10个柱子np.arange(1, 16) - 0.5表示将柱子的中心点设置为整数
        plt.xlabel("CQI Value")
        plt.ylabel("number of UEs")
        plt.title("CQI distribution histogram")
        plt.xticks(range(1, 16))
        plt.grid(axis="y")
        if CONFIG.simulation.save_info:
            plt.savefig(
                self.save_path + "//" + "CQI distribution.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def plot_mcs_distribution(self):
        """绘制 MCS 调制方式的统计情况"""
        unique_mcs, counts = np.unique(self.modulation, return_counts=True)
        plt.figure(figsize=(8, 5))
        plt.bar(unique_mcs, counts, color="green", alpha=0.7)  ## alpha表示透明度
        plt.xlabel("modulation index (MCS)")
        plt.ylabel("number of UEs")
        plt.title("MCS choice statistics")
        # 获取mcs_map中的值
        plt.xticks(unique_mcs)
        plt.grid(axis="y")
        if CONFIG.simulation.save_info:
            plt.savefig(
                self.save_path + "//" + "MCS distribution.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def show_hist_snr(self):
        """绘制SNR分布情况"""
        plt.figure(figsize=(8, 5))
        plt.hist(self.final_snr_list, bins=30, edgecolor="black", alpha=0.7)
        plt.xlabel("SNR (dB)")
        plt.ylabel("number of UEs")
        plt.title("Final SNR distribution histogram")
        plt.grid(axis="y")
        if CONFIG.simulation.save_info:
            plt.savefig(
                self.save_path + "//" + "Final SNR distribution.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def show_bler_analysis(self):
        """新增BLER相关可视化"""
        plt.figure(figsize=(15, 10))

        # BLER分布直方图
        plt.subplot(2, 2, 1)
        plt.hist(self.bler_values, bins=20, edgecolor="black")
        plt.title("BLER Distribution")
        plt.xlabel("BLER")
        plt.ylabel("User Count")

        # BLER vs SNR散点图
        plt.subplot(2, 2, 2)
        colors = ["red" if bler > 0.1 else "blue" for bler in self.bler_values]
        plt.scatter(self.final_snr_list, self.bler_values, c=colors, alpha=0.6)
        plt.title("BLER vs SNR")
        plt.xlabel("SNR (dB)")
        plt.ylabel("BLER")
        plt.grid(True)

        # 不同调制方式的平均BLER
        plt.subplot(2, 2, 3)
        # self.calculate_avg_bler()

        plt.bar(self.avg_bler.keys(), self.avg_bler.values())
        plt.title("Average BLER per Modulation")
        plt.xlabel("Modulation Scheme")
        plt.ylabel("Average BLER")

        # BLER-CQI关系热力图
        plt.subplot(2, 2, 4)
        cqis = sorted(self.cqi_bler.keys())
        avg_bler_per_cqi = [np.mean(self.cqi_bler[cqi]) for cqi in cqis]
        plt.plot(cqis, avg_bler_per_cqi, marker="o")
        plt.title("Average BLER vs CQI")
        plt.xlabel("CQI Index")
        plt.ylabel("Average BLER")
        plt.xticks(range(1, 16))
        plt.grid(True)
        plt.tight_layout()
        if CONFIG.simulation.save_info:
            plt.savefig(
                self.save_path + "//" + "BLER data.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def print_summary_stats(self):
        """打印关键统计指标"""
        print("\n=== BLER统计摘要 ===")
        print(f"平均BLER: {np.mean(self.bler_values):.2%}")
        print(f"BLER>10%的用户比例: {np.mean(np.array(self.bler_values) > 0.1):.2%}")
        print(f"最高BLER: {np.max(self.bler_values):.2%}")
        print(f"最低BLER: {np.min(self.bler_values):.2%}")

        # 各调制方式的BLER统计
        print("\n=== 各调制方式BLER ===")
        for mod, bler in self.avg_bler.items():
            print(f"{mod}: {bler:.2%}")
        print("\n=== 总指标 ===")
        print(f"理论吞吐量: {self.theoretical_throughput / 1e9:.4f} Gbps")
        print(
            f"结束时刻-仿真总吞吐量: {self.total_throughput / 1e9:.4f} Gbps,达理论值的{self.total_throughput / self.theoretical_throughput:.2%}"
        )
        time_mean_throughput = self.total_time_throughput / (CONFIG.simulation.tti_length)
        rate = time_mean_throughput / self.theoretical_throughput
        print(
            f"时域上平均-仿真总吞吐量: {time_mean_throughput / 1e9:.4f} "
            f"Gbps,达理论值的{rate:.2%}"
        )
        # print(f"用户数：{CONFIG.simulation.num_users} 平均吞吐量: {np.mean(self.throughputs) / 1e6:.4f} Mbps")
        print(f"平均时延: {self.avg_delay * 1e3} 毫秒")
        # 将以上信息存储为文本文件

        file_path = os.path.join(self.save_path, "results.txt")
        # 写入文件
        with open(file_path, "w") as f:
            f.write("=== BLER统计摘要 ===\n")
            f.write(f"平均BLER: {np.mean(self.bler_values):.2%}\n")
            f.write(
                f"BLER>10%的用户比例: {np.mean(np.array(self.bler_values) > 0.1):.2%}\n"
            )
            f.write(f"最高BLER: {np.max(self.bler_values):.2%}\n")
            f.write(f"最低BLER: {np.min(self.bler_values):.2%}\n")
            f.write("\n=== 各调制方式BLER ===\n")
            for mod, bler in self.avg_bler.items():
                f.write(f"{mod}: {bler:.2%}\n")
            f.write("\n=== 总指标 ===\n")
            f.write(f"理论吞吐量: {self.theoretical_throughput / 1e9:.4f} Gbps\n")
            f.write(
                f"结束时刻-仿真总吞吐量: {self.total_throughput / 1e9:.4f} Gbps,"
                f"达理论值的{self.total_throughput / self.theoretical_throughput:.2%}\n"
            )
            f.write(
                f"时域上平均-仿真总吞吐量: {time_mean_throughput / 1e9:.4f} "
                f"Gbps,达理论值的{rate:.2%}\n"
            )
            f.write(f"平均时延: {self.avg_delay * 1e3} 毫秒")

    def show_delay_distribution(self):
        """绘制时延分布情况"""
        plt.figure(figsize=(8, 5))
        plt.hist(self.transmission_time, bins=15, edgecolor="black", alpha=0.7)
        plt.xlabel("Transmission Time")
        plt.ylabel("number of UEs")
        plt.title("Transmission Time distribution histogram")
        plt.grid(axis="y")
        if CONFIG.simulation.save_info:
            plt.savefig(
                self.save_path + "//" + "delay distribution.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def show_snr_mcsindex(self):
        X = np.array(self.final_snr_list)
        Y = np.array(self.mcs_index)  # MCS索引从0开始
        # 画散点图
        plt.figure(figsize=(8, 5))
        plt.scatter(X, Y, c="blue", alpha=0.7)
        plt.xlabel("SNR (dB)")
        plt.ylabel("MCS")
        plt.title("SNR vs MCS index")
        plt.grid()
        if CONFIG.simulation.save_info:
            plt.savefig(
                self.save_path + "//" + "SNR-MCS.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def show_snr_efficiency(self):
        X = np.array(self.final_snr_list)
        Y = np.array(self.efficiency)  # MCS索引从0开始
        # 画散点图
        plt.figure(figsize=(8, 5))
        plt.scatter(X, Y, c="blue", alpha=0.7)
        plt.xlabel("SNR (dB)")
        plt.ylabel("efficiency")
        plt.title("SNR vs efficiency")
        plt.grid()
        if CONFIG.simulation.save_info:
            plt.savefig(
                self.save_path + "//" + "SNR-Efficiency.svg",
                format="svg",
                dpi=280,
            )
        # plt.show()

    def show_all_results(self):
        """调用所有的可视化函数"""
        if CONFIG.show.plot_hist_snr:
            self.show_hist_snr()
        if CONFIG.show.plot_throughput_distribution:
            self.plot_throughput_distribution()
        if CONFIG.show.show_delay_distribution:
            self.show_delay_distribution()
        if CONFIG.show.plot_cqi_distribution:
            self.plot_cqi_distribution()
        if CONFIG.show.plot_mcs_distribution:
            self.plot_mcs_distribution()
        if CONFIG.show.show_bler_analysis:
            self.show_bler_analysis()
        if CONFIG.show.print_summary_stats:
            self.print_summary_stats()
        if CONFIG.show.show_snr_mcsindex:
            self.show_snr_mcsindex()
        if CONFIG.show.show_snr_bijiao:
            self.cut_snr_bijiao()

    def save_data_for_training(self):
        if CONFIG.simulation.save_training_results:
            mode = CONFIG.ai.data_mode
            filename = {
                "snr_filename": mode + "_final_snr_list.npy",
                "mcs_filename": mode + "_mcs_index.npy",
            }
            np.save(
                self.save_path + "\\" + filename["snr_filename"], self.final_snr_list
            )
            np.save(self.save_path + "\\" + filename["mcs_filename"], self.mcs_index)

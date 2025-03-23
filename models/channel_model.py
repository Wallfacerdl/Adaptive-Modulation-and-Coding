# -*- coding: utf-8 -*-
"""用于生成初始SNR和演化SNR"""
# 小符同学
# python YYDS
# 开发时间： 2025/2/27 下午5:24
import matplotlib.pyplot as plt
from config.DefaultConfig import CONFIG
import numpy as np
import matplotlib

matplotlib.use('TkAgg')  # or 'Agg', 'Qt5Agg', etc.


class InitSNRGenerator:
    def __init__(self, num_users, median, sigma, low, high):
        self.num_users = num_users
        self.median = median
        self.sigma = sigma
        self.low = low
        self.high = high
        self.show_cut = True
        self.new_median = 0

    def generate(self):
        """
        生成正态分布的SNR值（3GPP阴影衰落模型）
        :return: SNR数组（dB）
        """
        samples = np.random.normal(self.median, self.sigma, self.num_users)
        if CONFIG.show.plot_hist_snr and self.show_cut:
            plt.subplot(1, 2, 1)
            # bins参数是指定bin(箱子)的个数，也就是总共有几条条状图
            plt.hist(samples, bins = 13, edgecolor = 'black', alpha = 0.7)
            plt.suptitle("SNR Distribution")
            plt.title("截断前")
        overflow_num = 0
        cut_samples = []
        for snr in samples:
            if snr > self.high:
                overflow_num += 1
                # print(snr)
                continue
            elif snr < self.low:
                overflow_num += 1
                continue
            cut_samples.append(snr)

        if CONFIG.show.plot_hist_snr and self.show_cut:
            plt.subplot(1, 2, 2)
            plt.hist(cut_samples, bins = 13, edgecolor = 'black', alpha = 0.7)
            plt.title("截断后")
            if CONFIG.simulation.save_info:
                import os
                from datetime import datetime
                # 如果存在results文件夹，则保存图片
                if not os.path.exists('results'):
                    os.makedirs('results')
                # 创建当前时间子文件夹
                timestamp = datetime.now().strftime('%Y%m%d_%H')
                results_dir = os.path.join('results', timestamp)
                if not os.path.exists(results_dir):
                    os.makedirs(results_dir)
                plt.savefig(os.path.join(results_dir, 'SNR distribution.png'))

            plt.show()

        self.new_median = np.mean(cut_samples)
        return {
            "values":        cut_samples,
            "overflow_rate": overflow_num / self.num_users,
            "new_median":    self.new_median
            }


class AR_SNR_Generator:
    """AR(1)信道模型，自动生成SNR序列"""

    def __init__(self, init_snr_db=20.0, alpha=0.9, sigma_db=4.0, noise_scale=1.0):
        """
        init_snr_db: 初始SNR值 (dB)
        alpha: 时间相关性系数 (0.9≈慢变，0.5≈快变)
        sigma_db: 波动标准差 (dB)
        noise_scale: 噪声放大系数
        """
        self.init_snr_db = init_snr_db
        self.current_snr = init_snr_db
        self.alpha = alpha
        self.sigma_ar = sigma_db * np.sqrt(1 - self.alpha**2) * noise_scale
        pass

    def next_snr(self):
        """输出下一时刻SNR"""
        # 使SNR围绕初始值波动
        self.current_snr = (self.alpha * self.current_snr + (1 - self.alpha) *
                            self.init_snr_db + np.random.normal(0, self.sigma_ar))
        if self.current_snr < CONFIG.channel.snr['init_range'][0]:
            self.current_snr = 0
        elif self.current_snr > CONFIG.channel.snr['init_range'][1]:
            self.current_snr = CONFIG.channel.snr['init_range'][1]
        return round(self.current_snr, 1)


if __name__ == '__main__':
    init_snr_sequences = InitSNRGenerator(1000, 15, 4, 0, 25).generate()
    print(init_snr_sequences["new_median"])

    init_snr_gen = init_snr_sequences["values"][0]
    print("初始SNR:", init_snr_gen)
    # 使用示例
    snr_gen = AR_SNR_Generator(init_snr_db = init_snr_gen, alpha = 0.9, sigma_db = 0.6)
    print("两百点采样SNR序列 (dB):")
    lst = []
    for _ in range(10000):
        snr_next = snr_gen.next_snr()
        lst.append(snr_next)
        if _ % 200 == 0:
            print(snr_next)
    # 均值
    print("均值:", np.mean(lst))

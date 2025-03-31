# 已弃用
import numpy as np
from utils.font_setting import font_setting

font_setting()
import pandas as pd

snr_values = np.load("../snr_values.npy")
mcs_index = np.load("../mcs_index.npy")
# import matplotlib.pyplot as plt
#
# # 绘制snr-mcs的散点图
# plt.figure(figsize = (8, 5))
# plt.scatter(snr_values, mcs_index, color = 'blue', alpha = 0.7)
# plt.xlabel("SNR (dB)")
# plt.ylabel("MCS index")
# plt.title("SNR-MCS relation")
# plt.grid(True)
# # plt.show()
"""将数据存储为dataframe文件"""
data = pd.DataFrame({"SNR": snr_values, "MCS": mcs_index})
# 按照snr的范围排序，并找出每个mcs中的最大和最小snr

# 按照SNR的范围排序
data_sorted = data.sort_values(by = "SNR")

# 找出每个MCS中的最大和最小SNR
mcs_snr_stats = data_sorted.groupby("MCS")["SNR"].agg(["min", "max"]).reset_index()
# 存储该数据结构
mcs_snr_stats.to_csv("../mcs_snr_stats.csv", index = False)

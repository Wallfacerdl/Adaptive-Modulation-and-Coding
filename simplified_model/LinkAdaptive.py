# -*- coding: utf-8 -*-

import os
import numpy as np

# 定义 SNR 值范围
snr_values = np.linspace(0, 30, 50)  # SNR 从 0 到 30dB，共 50 个点

# 定义调制方式及其频谱效率
modulations = ['BPSK', 'QPSK', '16-QAM']
spectral_efficiency = {
    'BPSK':   1,
    'QPSK':   2,
    '16-QAM': 4
    }


# 理论误码率公式 (仅用于演示，实际情况可能更复杂)
def theoretical_ber(snr, modulation):
    snr_linear = 10 ** (snr / 10)  # 将 SNR 转换为线性值
    if modulation == 'BPSK':
        return 0.5 * np.exp(-snr_linear)
    elif modulation == 'QPSK':
        return 0.5 * np.exp(-snr_linear / 2)
    elif modulation == '16-QAM':
        return 0.5 * np.exp(-snr_linear / 10)
    else:
        raise ValueError("未知调制方式")


# 生成每个 SNR 对应的调制方式指标
data = []
for snr in snr_values:
    for mod in modulations:
        ber = theoretical_ber(snr, mod)
        efficiency = spectral_efficiency[mod]
        data.append([snr, mod, ber, efficiency])

# 转为 NumPy 数组
data = np.array(data, dtype = object)

# 保存数据
current_dir = os.path.dirname(os.path.abspath(__file__))
np.save(os.path.join(current_dir, 'snr_modulation_data.npy'), data)
print("数据生成完成，保存为 snr_modulation_data.npy")

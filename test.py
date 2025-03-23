from scipy.optimize import curve_fit
import numpy as np


def sigmoid(x, snr_50, k):
    return 1 / (1 + np.exp(-k * (x - snr_50)))


# 示例：MCS=10的仿真数据
for snr in np.arange(0, 25, 0.1):
    bler = sigmoid(snr, 15.0, 1.42)
    print(f"SNR={snr}, BLER={bler:.4f}")
snr_samples = [5.0, 7.0, 9.0, 11.0, 13.0]
bler_samples = [0.95, 0.75, 0.30, 0.05, 0.01]

params, _ = curve_fit(sigmoid, snr_samples, bler_samples, p0 = [8.0, 1.0])
print(f"SNR_50={params[0]:.2f}, k={params[1]:.2f}")

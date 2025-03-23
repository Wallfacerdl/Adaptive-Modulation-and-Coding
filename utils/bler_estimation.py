# 小符同学
# python YYDS
# 开发时间： 2025/2/19 上午11:21
from math import erfc

import numpy as np


def estimate_bler(snr_db, cqi: int, mcs: dict) -> float:
    """
    Estimating the false block rate for a given SNR and modulation method\n
    :param mcs: 调制编码方式字典
    :param snr_db: SNR value in dB\n
    :param  cqi cqi index\n
    :return:float: 估算的BLER值（0.0~1.0）
    """
    choice = 2
    if choice == 1:
        # 方法1：基于经验公式
        # 预定每个数据块含有的比特数
        k = 1024
        modulation = mcs["modulation"]
        code_rate = mcs["CodeRate*1024"] / 1024
        if snr_db < 10:
            pass
        snr = 10 ** (snr_db / 10)  # 将 SNR 从 dB 转换为线性
        effective_snr = snr * code_rate
        if modulation == 'QPSK':
            ber = 0.5 * erfc(np.sqrt(effective_snr / 2))  # QPSK 的 BER 公式
        elif modulation == '16QAM':
            ber = (3 / 8) * erfc(np.sqrt(effective_snr / 10))
        elif modulation == '64QAM':
            ber = (7 / 24) * erfc(np.sqrt(effective_snr / 21))
        bler = 1 - (1 - ber) ** k  # BLER 的计算公式
        return bler  # BLER 的计算公式
    elif choice == 2:
        ## 方法2：基于Sigmoid曲线(隐式包含了编码增益）
        # 不同调制方式的S曲线参数
        # 每个CQI对应的Sigmoid参数（mid_x: BLER=0.5时的SNR, steepness: 曲线陡峭度）

        steepness = mcs["k"]
        mid_x = mcs["SNR_50"]
        exponent = steepness * (snr_db - mid_x)  # 确定S曲线的斜率和偏移量

        bler = 1 / (1 + np.exp(exponent))

        # 限制BLER范围
        return np.clip(bler, 0, 0.99)  # 最小1%，最大99%
    elif choice == 3:
        ## 方法2：基于Sigmoid曲线(隐式包含了编码增益）
        # 不同调制方式的S曲线参数
        # 每个CQI对应的Sigmoid参数（mid_x: BLER=0.5时的SNR, steepness: 曲线陡峭度）
        CQI_SIGMOID_PARAMS = {
            1:  {"mid_x": 2.5, "steepness": -0.90},  # QPSK低码率
            2:  {"mid_x": 4.0, "steepness": -0.92},
            3:  {"mid_x": 5.5, "steepness": -0.94},
            4:  {"mid_x": 7.0, "steepness": -0.96},
            5:  {"mid_x": 8.5, "steepness": -1.10},  # 16QAM
            6:  {"mid_x": 9, "steepness": -1.12},
            7:  {"mid_x": 9.5, "steepness": -1.14},
            8:  {"mid_x": 10, "steepness": -1.16},
            9:  {"mid_x": 10.5, "steepness": -1.30},  # 64QAM
            10: {"mid_x": 11, "steepness": -1.32},
            11: {"mid_x": 12, "steepness": -1.34},
            12: {"mid_x": 12.5, "steepness": -1.36},
            13: {"mid_x": 13, "steepness": -1.38},
            14: {"mid_x": 14.5, "steepness": -1.40},
            15: {"mid_x": 15, "steepness": -1.42},  # 表示64QAM在SNR≈15dB处BLER=0.5
            }

        # 获取参数
        params = CQI_SIGMOID_PARAMS[cqi]
        # Sigmoid计算
        exponent = -1 * params["steepness"] * (snr_db - params["mid_x"])  # 确定S曲线的斜率和偏移量
        bler = 1 / (1 + np.exp(exponent))
        return np.clip(bler, 0.001, 0.99)  # 最小1%，最大99%
    elif choice == 4:
        ## 方法2：基于Sigmoid曲线(隐式包含了编码增益）
        # 不同调制方式的S曲线参数
        # 每个CQI对应的Sigmoid参数（mid_x: BLER=0.5时的SNR, steepness: 曲线陡峭度）
        CQI_SIGMOID_PARAMS = {
            1:  {"alpha_0": 28.08, "alpha_1": 9.71},  # QPSK低码率
            2:  {"alpha_0": 20.59, "alpha_1": 11.05},
            3:  {"alpha_0": 15.31, "alpha_1": 12.89},
            4:  {"alpha_0": 11.09, "alpha_1": 14.45},
            5:  {"alpha_0": 8.05, "alpha_1": 17.12},  # 16QAM
            6:  {"alpha_0": 6.56, "alpha_1": 20.56},
            7:  {"alpha_0": 2.48, "alpha_1": 16.07},
            8:  {"alpha_0": 2.39, "alpha_1": 22.83},
            9:  {"alpha_0": 1.26, "alpha_1": 18.74},  # 64QAM
            10: {"alpha_0": 0.67, "alpha_1": 20.02},
            11: {"alpha_0": 0.40, "alpha_1": 18.36},
            12: {"alpha_0": 0.26, "alpha_1": 16.62},
            13: {"alpha_0": 0.17, "alpha_1": 16.18},
            14: {"alpha_0": 0.04, "alpha_1": 7.02},
            15: {"alpha_0": 0.03, "alpha_1": 8.84},  # 表示64QAM在SNR≈15dB处BLER=0.5
            }

        # 获取参数
        params = CQI_SIGMOID_PARAMS[cqi]
        # Sigmoid计算
        exponent = params["alpha_0"] * snr_db - params["alpha_1"]  # 确定S曲线的斜率和偏移量
        bler = 1 / (1 + np.exp(exponent))
        return np.clip(bler, 0.001, 0.99)  # 最小1%，最大99%

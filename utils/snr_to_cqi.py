# snr_to_cqi.py
import numpy as np


def snr_to_cqi(snr_db):
    """
    根据SNR值返回CQI索引（基于64QAM调制最大化的场景）；此映射关系为人为规定的，并非标准
    :param snr_db: 转化为db的SNR值
    :return: 返回CQI
    """
    if snr_db < 0:
        return 1  # 无效SNR，最低CQI
    elif 0 <= snr_db < 2.5:
        return 1  # 边缘覆盖
    elif 2.5 <= snr_db < 4.0:
        return 2  # 弱信号
    elif 4.0 <= snr_db < 5.5:
        return 3  # 基础语音
    elif 5.5 <= snr_db < 7.0:
        return 4  # 低速数据
    elif 7.0 <= snr_db < 8.5:
        return 5  # 中速数据
    elif 8.5 <= snr_db < 10.0:
        return 6  # 中速视频
    elif 10.0 <= snr_db < 12.0:
        return 7  # 高速数据
    elif 12.0 <= snr_db < 14.0:
        return 8  # 高密度城区
    elif 14.0 <= snr_db < 16.0:
        return 9  # 热点中高速
    elif 16.0 <= snr_db < 18.0:
        return 10  # 室内高吞吐
    elif 18.0 <= snr_db < 20.0:
        return 11  # 近点高速率
    elif 20.0 <= snr_db < 21.5:
        return 12  # 优质信道高频谱
    elif 21.5 <= snr_db < 23.0:
        return 13  # 极近点峰值速率
    elif 23.0 <= snr_db < 24.0:
        return 14  # 实验室环境
    else:
        return 15  # 理论极限

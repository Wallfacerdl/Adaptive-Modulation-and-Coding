# 小符同学
# python YYDS
# 开发时间： 2025/2/24 下午5:54
# 读取mcs_snr_stats.csv文件，将SNR值映射到MCS
import pandas as pd


def ai_get_mcs_index(snr_db):
    """
    根据SNR范围将新输入的SNR值映射到MCS
    :param snr_db: 新的SNR值
    :return: 映射后的MCS索引
    """
    choice = 'ai-model'
    if choice == 'table':
        mcs_snr_stats = pd.read_csv("mcs_snr_stats.csv")

        for _, row in mcs_snr_stats.iterrows():
            if row['min'] <= snr_db <= row['max']:
                return row['MCS']
        # 如果没有找到匹配的MCS，返回最接近的较低MCS
        closest_mcs = mcs_snr_stats[mcs_snr_stats['min'] <= snr_db].iloc[-1]['MCS']
        return closest_mcs

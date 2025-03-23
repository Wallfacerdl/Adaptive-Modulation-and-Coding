# cqi_to_mcs.py

from utils.mapping import cqi_to_mcs_map


def cqi_to_mcs(cqi: int) -> dict:
    """
    根据CQI返回mcs
    :param cqi: [1, 15] 之间的整数，表示信道质量的相对值
    :return:含有mcs、调制阶数、编码率和频谱效率的字典
    """
    # 调制方式和编码率映射表
    """字典解释：
    modulation: 调制方式
    order: 调制阶数
    CodeRate*1024: 编码率（1024）
    efficiency: 频谱效率=CodeRate * log2(order)
    CodeRate: 编码率= (TBSize +CRC)/( Bits number after RateMatching)
    """
    ## 3GPP TS 36.213 Table
    ## 原理：随着CQI值的提高，信道质量得到改善，系统可以选择更高的编码率，从而减少前向纠错码的冗余部分，提升有效信息的比例，进而提高编码率。
    ## 低频谱效率（Low SE） 64QAM表适用于需要可靠数据传输的应用，如URLLC类应用。该表包括了频谱效率低的MCS，即降低了编码速率，增加了信道编码冗余。
    ## 这里的efficiency是指理论频谱效率，即CodeRate * order

    # 返回默认值（QPSK, 2码元, 编码率 0.1），以防 CQI 不在映射表中
    return cqi_to_mcs_map.get(cqi,
                              {"modulation": "QPSK", "order": 2, "CodeRate*1024": 78,
                               "efficiency": 0.1523, "CodeRate": 0.076})  # 默认返回最低mcs

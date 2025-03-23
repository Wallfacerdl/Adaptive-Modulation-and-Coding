# 小符同学
# python YYDS
# 开发时间： 2025/2/24 下午2:10
cqi_to_mcs_map = {
    # CQI 1-4: QPSK (0.0~7.0 dB)
    1:  {"modulation": "QPSK", "order": 2, "CodeRate*1024": 78, "efficiency": 0.1523, "CodeRate": 0.076},  # 0.0 ~2.5 dB
    2:  {"modulation": "QPSK", "order": 2, "CodeRate*1024": 120, "efficiency": 0.2344, "CodeRate": 0.120},  # 2.5~4.0 dB
    3:  {"modulation": "QPSK", "order": 2, "CodeRate*1024": 193, "efficiency": 0.3770, "CodeRate": 0.193},  # 4.0~5.5 dB
    4:  {"modulation": "QPSK", "order": 2, "CodeRate*1024": 308, "efficiency": 0.6016, "CodeRate": 0.308},  # 5.5~7.0 dB

    # CQI 5-8: 16QAM (7.0~14.0 dB)
    5:  {"modulation": "16QAM", "order": 4, "CodeRate*1024": 220, "efficiency": 0.8594, "CodeRate": 0.220},  # 7.0~8.5 dB
    6:  {"modulation": "16QAM", "order": 4, "CodeRate*1024": 300, "efficiency": 1.1719, "CodeRate": 0.300},  # 8.5~10.0 dB
    7:  {"modulation": "16QAM", "order": 4, "CodeRate*1024": 440, "efficiency": 1.7188, "CodeRate": 0.440},  # 10.0~12.0 dB
    8:  {"modulation": "16QAM", "order": 4, "CodeRate*1024": 590, "efficiency": 2.3047, "CodeRate": 0.590},  # 12.0~14.0 dB

    # CQI 9-15: 64QAM (14.0~25.0 dB)
    9:  {"modulation": "64QAM", "order": 6, "CodeRate*1024": 370, "efficiency": 2.1680, "CodeRate": 0.370},  # 14.0~16.0 dB
    10: {"modulation": "64QAM", "order": 6, "CodeRate*1024": 480, "efficiency": 2.8125, "CodeRate": 0.480},  # 16.0~18.0 dB
    11: {"modulation": "64QAM", "order": 6, "CodeRate*1024": 600, "efficiency": 3.5156, "CodeRate": 0.600},  # 18.0~20.0 dB
    12: {"modulation": "64QAM", "order": 6, "CodeRate*1024": 730, "efficiency": 4.2773, "CodeRate": 0.730},  # 20.0~21.5 dB
    13: {"modulation": "64QAM", "order": 6, "CodeRate*1024": 820, "efficiency": 4.8047, "CodeRate": 0.820},  # 21.5~23.0 dB
    14: {"modulation": "64QAM", "order": 6, "CodeRate*1024": 890, "efficiency": 5.2148, "CodeRate": 0.890},  # 23.0~24.0 dB
    15: {"modulation": "64QAM", "order": 6, "CodeRate*1024": 948, "efficiency": 5.5547, "CodeRate": 0.948},  # 24.0~25.0 dB
    }
# 编码率等于码率除以调制阶数
# order = log2(M) M为码元数量，QPSK为2，16QAM为4，64QAM为6
# （R)：CodeRate：常见的编码率有1/2、2/3、3/4、5/6、7/8等，即CRC校验码和数据比例
# effieciency = CodeRate * order
mcs_index_map = {
    # ---------------------------- QPSK (MCS 0-9) ----------------------------
    0:  {"index": 0, "order": 2, "modulation": "QPSK", "CodeRate*1024": 120, "efficiency": 0.2344, "SNR_50": 0, "k": 0.8},  # 编码率为1/2
    1:  {"index": 1, "order": 2, "modulation": "QPSK", "CodeRate*1024": 157, "efficiency": 0.3066, "SNR_50": 0.5, "k": 0.9},  # 编码率为3/4
    2:  {"index": 2, "order": 2, "modulation": "QPSK", "CodeRate*1024": 193, "efficiency": 0.3770, "SNR_50": 1.5, "k": 1.0},  # 编码率为1/2
    3:  {"index": 3, "order": 2, "modulation": "QPSK", "CodeRate*1024": 251, "efficiency": 0.4902, "SNR_50": 2.5, "k": 1.1},  # 编码率为3/4
    4:  {"index": 4, "order": 2, "modulation": "QPSK", "CodeRate*1024": 308, "efficiency": 0.6016, "SNR_50": 3, "k": 1.2},  # 编码率为1/2
    5:  {"index": 5, "order": 2, "modulation": "QPSK", "CodeRate*1024": 379, "efficiency": 0.7402, "SNR_50": 4.5, "k": 1.3},
    6:  {"index": 6, "order": 2, "modulation": "QPSK", "CodeRate*1024": 449, "efficiency": 0.8770, "SNR_50": 5.5, "k": 1.4},
    7:  {"index": 7, "order": 2, "modulation": "QPSK", "CodeRate*1024": 526, "efficiency": 1.0273, "SNR_50": 6.0, "k": 1.5},
    8:  {"index": 8, "order": 2, "modulation": "QPSK", "CodeRate*1024": 602, "efficiency": 1.1758, "SNR_50": 6.5, "k": 1.6},
    9:  {"index": 9, "order": 2, "modulation": "QPSK", "CodeRate*1024": 679, "efficiency": 1.3262, "SNR_50": 7.0, "k": 1.7},

    # ---------------------------- 16QAM (MCS 10-16) ----------------------------
    10: {"index": 10, "order": 4, "modulation": "16QAM", "CodeRate*1024": 340, "efficiency": 1.3281, "SNR_50": 8.0, "k": 1.8},
    11: {"index": 11, "order": 4, "modulation": "16QAM", "CodeRate*1024": 378, "efficiency": 1.4766, "SNR_50": 8.5, "k": 1.9},
    12: {"index": 12, "order": 4, "modulation": "16QAM", "CodeRate*1024": 434, "efficiency": 1.6953, "SNR_50": 9.0, "k": 2.0},
    13: {"index": 13, "order": 4, "modulation": "16QAM", "CodeRate*1024": 490, "efficiency": 1.9141, "SNR_50": 9.5, "k": 2.1},
    14: {"index": 14, "order": 4, "modulation": "16QAM", "CodeRate*1024": 553, "efficiency": 2.1602, "SNR_50": 10.0, "k": 2.2},
    15: {"index": 15, "order": 4, "modulation": "16QAM", "CodeRate*1024": 616, "efficiency": 2.4063, "SNR_50": 10.5, "k": 2.3},
    16: {"index": 16, "order": 4, "modulation": "16QAM", "CodeRate*1024": 658, "efficiency": 2.5703, "SNR_50": 11.0, "k": 2.4},

    # ---------------------------- 64QAM (MCS 17-28) ----------------------------
    17: {"index": 17, "order": 6, "modulation": "64QAM", "CodeRate*1024": 438, "efficiency": 2.5664, "SNR_50": 12.0, "k": 2.5},
    18: {"index": 18, "order": 6, "modulation": "64QAM", "CodeRate*1024": 466, "efficiency": 2.7305, "SNR_50": 12.5, "k": 2.6},
    19: {"index": 19, "order": 6, "modulation": "64QAM", "CodeRate*1024": 517, "efficiency": 3.0293, "SNR_50": 13.0, "k": 2.7},
    20: {"index": 20, "order": 6, "modulation": "64QAM", "CodeRate*1024": 567, "efficiency": 3.3223, "SNR_50": 13.5, "k": 2.8},
    21: {"index": 21, "order": 6, "modulation": "64QAM", "CodeRate*1024": 616, "efficiency": 3.6094, "SNR_50": 14.0, "k": 2.9},
    22: {"index": 22, "order": 6, "modulation": "64QAM", "CodeRate*1024": 666, "efficiency": 3.9023, "SNR_50": 14.5, "k": 3.0},
    23: {"index": 23, "order": 6, "modulation": "64QAM", "CodeRate*1024": 719, "efficiency": 4.2129, "SNR_50": 15.0, "k": 3.1},
    24: {"index": 24, "order": 6, "modulation": "64QAM", "CodeRate*1024": 772, "efficiency": 4.5234, "SNR_50": 15.5, "k": 3.2},
    25: {"index": 25, "order": 6, "modulation": "64QAM", "CodeRate*1024": 822, "efficiency": 4.8047, "SNR_50": 16.0, "k": 3.3},
    26: {"index": 26, "order": 6, "modulation": "64QAM", "CodeRate*1024": 873, "efficiency": 5.1152, "SNR_50": 16.5, "k": 3.4},
    27: {"index": 27, "order": 6, "modulation": "64QAM", "CodeRate*1024": 910, "efficiency": 5.3320, "SNR_50": 17.0, "k": 3.5},
    28: {"index": 28, "order": 6, "modulation": "64QAM", "CodeRate*1024": 948, "efficiency": 5.5547, "SNR_50": 17.5, "k": 3.6},
    }

# 小符同学
# python YYDS
# 开发时间： 2025/2/24 上午11:03
from utils.mapping import mcs_index_map, cqi_to_mcs_map


def get_initial_mcs_index(cqi: int, alpha = 0.1) -> int:
    """
    根据CQI返回mcs
    :param alpha: 容许的频谱效率误差
    :param cqi: [1, 15] 之间的整数，表示信道质量的相对值
    :return:mcs_index
    """
    # 1. 获取CQI建议参数
    cqi_dict = cqi_to_mcs_map.get(cqi)
    if not cqi_dict:
        raise ValueError  # 无效CQI返回最低MCS

    # 调制方式优先级字典（直接内联使用）

    # 2. 筛选候选MCS
    candidates = []
    for mcs_idx in mcs_index_map:
        mcs_dict = mcs_index_map[mcs_idx]

        # 检查调制方式兼容性和频谱效率约束
        if (mcs_dict["order"] <= cqi_dict["order"]) and \
                (mcs_dict["efficiency"] <= cqi_dict["efficiency"] * (1 + alpha)):
            candidates.append((mcs_idx, mcs_dict))
    # 3. 选择最优MCS：频谱效率最高 -> 码率最低
    if candidates:
        candidates.sort(key = lambda x: (-x[1]["efficiency"], x[1]["CodeRate*1024"]))
        return candidates[0][0]
    else:
        return 0


if __name__ == "__main__":
    test_cases = range(1, 16)
    for cqi in test_cases:
        mcs = get_initial_mcs_index(cqi)
        print(f"CQI={cqi} -> MCS={mcs}")

# 小符同学
# python YYDS
# 开发时间： 2025/2/20 上午10:31
import numpy as np


class BLERCalculator:
    def __init__(self, modulation, bler_values):
        self.avg_bler = {}  # 用于存储不同调制方式的平均BLER
        self.modulation = modulation
        self.bler_values = bler_values

    def calculate_avg_bler(self):
        mod_bler = {}  # 用于存储不同调制方式的BLER
        for mod, bler in zip(self.modulation, self.bler_values):
            mod_bler.setdefault(mod, []).append(bler)  # 将bler值添加到对应的modulation中
        self.avg_bler = {mod: np.mean(vals) for mod, vals in mod_bler.items()}
        return self.avg_bler

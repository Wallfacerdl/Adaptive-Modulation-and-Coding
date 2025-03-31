# models/link_adaptation.py
from utils.mapping import mcs_index_map
from utils.get_mcs_index import get_initial_mcs_index
from utils.ai_get_mcs_index import ai_get_mcs_index
from DL.train_wrapper import AIMSController
from config.DefaultConfig import CONFIG

class LinkAdaptation:
    def __init__(self, strategy):
        self.strategy = strategy  # 目前可以扩展更多策略
        self.mcs_su_table = []  # 用于存放查表法的MCS表
        if self.strategy == 'DNN':
            import os
            print('当前目录:', os.getcwd()) # 通常为工程根目录
            pth_path = os.path.join(os.getcwd(), 'DL', 'results')
            print('模型路径:', pth_path)
            # 要读取的模型文件名
            pth_name = f'{CONFIG.ai.pth_time}_{CONFIG.ai.model_name[:-4]}_{CONFIG.ai.data_mode}.pth'
            self.controller = AIMSController(pth_path + "\\" + pth_name)  # DNN模型

    def select_mcs(self, user):
        if self.strategy == '查表':
            # 默认策略：使用查表法--根据CQI选择MCS
            # return cqi_to_mcs(cqi)
            if not user.update:  # 初始化
                if mcs_index_map not in self.mcs_su_table:
                    self.mcs_su_table.append(mcs_index_map)
                return mcs_index_map[get_initial_mcs_index(user.cqi)]
            else:
                return mcs_index_map[user.mcs_index]
        elif self.strategy == 'DNN':
            return mcs_index_map[self.controller.safe_select_mcs(user.snr)]
        else:
            raise ValueError('无效的策略')

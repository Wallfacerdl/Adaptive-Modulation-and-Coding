# 小符同学
# python YYDS
# 开发时间： 2025/2/18 下午4:00
# 与现有仿真的对接层
import torch
from DL.training import SNRMCSModel
from config.DefaultConfig import CONFIG


class MCSPredictor:
    def __init__(self, model_path):
        # 加载保存的参数
        checkpoint = torch.load(model_path)
        self.model = SNRMCSModel()  # 需要先定义模型结构
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()  # 设置为评估模式

        # 加载归一化参数
        self.min_snr = checkpoint['normalization_params']['min_snr']
        self.max_snr = checkpoint['normalization_params']['max_snr']

    def normalize(self, snr):
        """将SNR归一化到[0,1]区间"""
        return (snr - self.min_snr) / (self.max_snr - self.min_snr)


class AIMSController:
    def __init__(self, model_path):
        self.predictor = MCSPredictor(model_path)

    def select_mcs(self, snr):
        """AI驱动选择最优MCS"""
        # 输入预处理
        normalized_snr = self.predictor.normalize(snr)
        input_tensor = torch.tensor([normalized_snr], dtype = torch.float32)
        input_tensor = input_tensor.unsqueeze(0)  # 形状从 [1] → [1,1]
        # 模型推理
        with torch.no_grad():
            output = self.predictor.model(input_tensor)
            predicted_mcs = torch.argmax(output).item()

        # 后处理（确保在有效范围内）
        final_mcs = max(0, min(predicted_mcs, 28))
        return final_mcs

    def safe_select_mcs(self, snr):
        """带异常处理的稳健版本"""
        try:
            # 检查SNR输入有效性
            snr_min = CONFIG.channel.snr["init_range"][0]
            snr_max = CONFIG.channel.snr["init_range"][1]
            if not (snr_min <= snr <= snr_max):
                print(f"警告：SNR {snr}超出训练范围[{snr_min}, {snr_max}]")
                return self.fallback_select_mcs(snr)

            # 正常推理流程
            return self.select_mcs(snr)

        except Exception as e:
            print(f"模型推理失败: {str(e)}")
            return -1
            # return legacy_select_mcs(snr)  # 回退到传统方法

    def fallback_select_mcs(self, snr):
        """超出训练范围时的处理策略"""
        if snr < self.min_snr:
            return 0  # 最低MCS
        else:
            return 28  # 最高MCS


def DL_select_mcs(snr_db):
    controller = AIMSController('mcs_predictor_params.pth')
    ai_mcs = controller.safe_select_mcs(snr)
    return ai_mcs
    # legacy_mcs = legacy_select_mcs(snr)
    # print(f"SNR={snr}dB | AI选择={ai_mcs} ")

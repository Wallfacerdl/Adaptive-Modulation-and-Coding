# 小符同学
# python YYDS
# 开发时间： 2025/2/25 上午9:56
import numpy as np
from utils.snr_to_cqi import snr_to_cqi
from utils.cqi_to_mcs import cqi_to_mcs
from utils.mapping import mcs_index_map
from utils.bler_estimation import estimate_bler
from utils.font_setting import font_setting

font_setting()
choice = 0  # 选择是否生成数据，0为直接加载数据，1为生成数据
# 3.1 网络架构
import torch.nn as nn
import torch

# Check if GPU is available

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# data_path = '/Users/delongfu/Library/CloudStorage/OneDrive-个人/SDE/3_Project/Adaptive Modulation and Coding/'
pth_name = 'mcs_predictor_params_simplified'
data_path = r'E:\OneDrive\SDE\3_Project\Adaptive Modulation and Coding'


class SNRMCSModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1, 64),  # 输入SNR
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 29)  # 输出29个MCS的概率
            )

    def forward(self, x):
        return self.layers(x)


if __name__ == '__main__':

    if choice == 0:
        """直接加载数据"""
        # 查看results目录下的最近日期是否有.npy文件，读取日期里面最接近的数据
        path = '../results/'
        # 获取results目录下的所有子路径
        results_dir = '20250315_16'
        path = path + results_dir + '/'

        # snr = np.load(path + 'snr_values.npy')
        # mcs_index_labels = np.load(path + 'mcs_index.npy')
        snr = np.load(data_path + '/snr_values.npy')
        mcs_index_labels = np.load(data_path + '/mcs_index.npy')

    else:
        """生成数据"""


        def snr_to_mcs(snr_db):
            for mcs_index_labels in reversed(range(29)):
                mcs = mcs_index_map[mcs_index_labels]
                bler = estimate_bler(snr_db, snr_to_cqi(snr_db), mcs)
                if bler <= 0.1:
                    return mcs_index_labels
            return 0


        snr = np.linspace(0, 25, 10000)  # 均匀采样
        mcs_index_labels = [snr_to_mcs(snr_db) for snr_db in snr]


    ## 3.2 输入输出处理
    # 输入归一化
    def normalize_snr(snr):
        return snr / 25.0  # 5~30 → 0~1


    # 输出处理
    def postprocess(output):
        return torch.argmax(output, dim = 1)  # 取概率最大的MCS


    ## 4.训练配置
    # 损失函数与优化器
    # 实例化模型
    model = SNRMCSModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr = 1e-3)

    # 数据集划分
    from sklearn.model_selection import train_test_split

    X_train, X_val, y_train, y_val = train_test_split(
        snr, mcs_index_labels, test_size = 0.2, random_state = 42
        )
    ## 5.训练过程
    # 转换为PyTorch张量
    train_dataset = torch.utils.data.TensorDataset(
        torch.FloatTensor([normalize_snr(x) for x in X_train]),
        torch.LongTensor(y_train)
        )

    # 数据加载器
    train_loader = torch.utils.data.DataLoader(
        dataset = train_dataset,
        batch_size = 32,
        shuffle = True
        )

    # 训练循环
    for epoch in range(100):
        flag = False
        for batch_x, batch_y in train_loader:
            flag = True
            outputs = model(batch_x.unsqueeze(1))  # 输入形状(batch,1)
            loss = criterion(outputs, batch_y)  # 计算损失
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        # 每个epoch结束后打印损失
        if flag:
            print(f'Epoch {epoch}, Loss: {loss.item()}')

    ## 6.1 性能评估——准确率计算
    with torch.no_grad():
        val_inputs = torch.FloatTensor([normalize_snr(x) for x in X_val])
        predictions = postprocess(model(val_inputs.unsqueeze(1)))
        accuracy = (predictions == torch.LongTensor(y_val)).float().mean()

    print(f"验证集准确率: {accuracy * 100:.2f}%")
    ## 可视化
    import matplotlib.pyplot as plt

    plt.figure(figsize = (10, 6))
    plt.scatter(X_val, y_val, label = '理论最优', alpha = 0.6)
    plt.scatter(X_val, predictions.numpy(), label = 'DNN预测', marker = 'x')
    plt.xlabel('SNR (dB)')
    plt.ylabel('最优MCS')
    plt.legend()
    plt.show()
    # 保存完整模型
    torch.save({
        'model_state_dict':     model.state_dict(),
        'normalization_params': {'min_snr': 0, 'max_snr': 25}
        }, pth_name + '.pth')

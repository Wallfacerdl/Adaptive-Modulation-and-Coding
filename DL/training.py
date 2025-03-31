# 小符同学
# python YYDS
# 开发时间： 2025/2/25 上午9:56
import numpy as np
from utils.snr_to_cqi import snr_to_cqi
from utils.mapping import mcs_index_map
from utils.bler_estimation import estimate_bler
from utils.font_setting import font_setting
from config.DefaultConfig import CONFIG
import torch.nn as nn
import torch

"""预设参数"""
mode = "Lite"  # 'Lite' or 'Complex'
dir = "20250330_20-48" + f"_查表_{mode}/"  # 数据集来自于查表法生成的仿真数据


class SNRMCSModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(1, 64),  # 输入SNR
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 29),  # 输出29个MCS的概率
        )

    def forward(self, x):
        return self.layers(x)


if __name__ == "__main__":
    font_setting()
    choice = 0  # 选择是否生成数据，0为直接加载数据，1为生成数据

    # 预准备：Check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if choice == 0:
        """直接加载数据"""
        """获取路径"""
        import os

        cur_path = os.path.abspath(__file__)  # 当前运行文件的绝对路径
        # 获取当前目录的上一级目录
        cur_path = os.path.abspath(os.path.join(cur_path, ".."))

        # 设置为工作目录(到DL层级)
        os.chdir(cur_path)
        # print('工作目录',cur_path)
        # 如果没有results文件夹，则创建
        if not os.path.exists(cur_path + "/results/"):
            os.makedirs(cur_path + "/results/")
        save_path = cur_path + "/results/"
        # print('模型保存路径',pth_save_path)

        # 获取当前文件所在的上两级目录
        project_path = os.path.abspath(os.path.join(cur_path, ".."))
        # print('项目目录',project_path)

        # 要生成的模型所在的目录
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H-%M")
        model_name = CONFIG.ai.model_name[:-4]  # 去掉后缀
        file_name = timestamp + "_" + model_name + f"_{mode}"

        data_path = project_path + "/results/" + dir
        """获取文件名"""

        snr_file_path = data_path + mode + "_final_snr_list.npy"
        mcs_file_path = data_path + mode + "_mcs_index.npy"
        try:
            snr = np.load(snr_file_path)
            mcs_index_labels = np.load(mcs_file_path)
        except FileNotFoundError:
            print("文件未找到，有可能是运行main函数时设置了不保存仿真结果")
            exit(1)

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
        return torch.argmax(output, dim=1)  # 取概率最大的MCS

    ## 4.训练配置
    # 损失函数与优化器
    # 实例化模型
    model = SNRMCSModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # 数据集划分
    from sklearn.model_selection import train_test_split

    X_train, X_val, y_train, y_val = train_test_split(
        snr, mcs_index_labels, test_size=0.2, random_state=42
    )
    ## 5.训练过程
    # 转换为PyTorch张量
    train_dataset = torch.utils.data.TensorDataset(
        torch.FloatTensor([normalize_snr(x) for x in X_train]),
        torch.LongTensor(y_train),
    )

    # 数据加载器
    train_loader = torch.utils.data.DataLoader(
        dataset=train_dataset, batch_size=32, shuffle=True
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
            print(f"Epoch {epoch}, Loss: {loss.item()}")

    ## 6.1 性能评估——准确率计算
    with torch.no_grad():
        val_inputs = torch.FloatTensor([normalize_snr(x) for x in X_val])
        predictions = postprocess(model(val_inputs.unsqueeze(1)))
        accuracy = (predictions == torch.LongTensor(y_val)).float().mean()

    print(f"验证集准确率: {accuracy * 100:.2f}%")
    ## 可视化
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.scatter(X_val, y_val, label="理论最优", alpha=0.6)
    plt.scatter(X_val, predictions.numpy(), label="DNN预测", marker="x")
    plt.xlabel("SNR (dB)")
    plt.ylabel("最优MCS")
    plt.legend()
    plt.savefig(save_path + "\\" + file_name + ".svg", format="svg", dpi=280)
    plt.show()
    # 保存完整模型
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "normalization_params": {"min_snr": 0, "max_snr": 25},
        },
        save_path + "\\" + file_name + ".pth",
    )

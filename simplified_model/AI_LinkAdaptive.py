# -*- coding: utf-8 -*-
from utils.font_setting import font_setting
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import time

font_setting()
# 加载数据
current_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(current_dir, 'snr_modulation_data.npy')
if not os.path.exists(data_file):
    raise FileNotFoundError("数据文件未找到，请先运行第一个文件生成数据！")

data = np.load(data_file, allow_pickle = True)

# 数据预处理
snr_values = np.array([row[0] for row in data])  # SNR 值
modulation_labels = np.array([row[1] for row in data])  # 调制方式
ber_values = np.array([row[2] for row in data])  # BER 值
efficiency_values = np.array([row[3] for row in data])  # 频谱效率

# 构造输入特征和目标标签
X = np.vstack((snr_values, ber_values)).T
y = modulation_labels

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)

# 训练模型
print("开始训练模型...")
model = RandomForestClassifier(n_estimators = 50, random_state = 42)
start_time = time.time()
model.fit(X_train, y_train)

# 显示进度
for i in range(101):  # 假装显示训练进度
    time.sleep(0.02)
    print(f"\r训练进度: {i}%", end = "")

print("\n模型训练完成！")
print(f"训练时间: {time.time() - start_time:.2f} 秒")

# 测试模型
print("\n开始测试模型...")
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

# 输出测试结果
print(f"模型测试准确率: {accuracy:.2%}")
print("\n部分测试样本预测结果：")
for i in range(5):  # 打印前 5 个测试样本
    snr, ber = X_test[i]
    actual = y_test[i]
    predicted = predictions[i]
    print(f"SNR: {snr:.1f} dB, 理论 BER: {ber:.2e}, 实际调制: {actual}, 预测调制: {predicted}")

# 可视化测试集预测结果
plt.figure(figsize = (12, 6))

# 绘制调制方式的预测分布
snr_test = X_test[:, 0]  # 测试集中的 SNR 值
plt.scatter(snr_test, predictions, c = 'b', label = "预测调制方式", alpha = 0.6)
plt.scatter(snr_test, y_test, c = 'r', label = "实际调制方式", alpha = 0.6, marker = 'x')
plt.xlabel("SNR (dB)")
plt.ylabel("调制方式")
plt.title("模型预测 vs 实际调制方式")
plt.legend()
plt.grid()
# plt.show()

# 性能曲线可视化
plt.figure(figsize = (12, 6))

# 绘制理论 BER 曲线
modulations = ['BPSK', 'QPSK', '16-QAM']
colors = ['blue', 'green', 'orange']
for mod, color in zip(modulations, colors):
    ber_theoretical = [10 ** (-snr / 10) if mod == 'BPSK' else
                       0.5 * np.exp(-10 ** (snr / 10)) if mod == 'QPSK' else
                       0.5 * np.exp(-10 ** (snr / 10) / 10) for snr in snr_values]
    plt.plot(snr_values, ber_theoretical, label = f"{mod} 理论 BER", color = color)

# 绘制模型推荐调制方式的 SNR 分布
plt.scatter(snr_test, predictions, c = 'black', label = "模型推荐调制方式", alpha = 0.6, s = 10)

plt.xlabel("SNR (dB)")
plt.ylabel("BER")
plt.title("理论 BER 曲线与模型推荐的调制方式")
plt.yscale("log")  # 使用对数坐标显示 BER
plt.legend()
plt.grid()
# plt.show()

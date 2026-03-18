# 项目上下文文档 - 自适应调制和编码（AMC）仿真系统

## 项目概述

本项目是一个用于研究无线通信系统中自适应调制和编码（Adaptive Modulation and Coding, AMC）技术的仿真系统。该项目通过仿真和深度学习方法，探索在不同信道条件下如何动态选择最优的调制和编码方案（MCS），以最大化系统吞吐量并满足服务质量（QoS）要求。

### 核心技术栈

- **Python 3.11+**：主要开发语言
- **Sionna 0.19.1**：用于物理层通信链路模拟的开源库
- **TensorFlow 2.15.1 / Keras 2.15.0**：深度学习框架
- **PyTorch**：用于训练 DNN 模型
- **NumPy, SciPy, Matplotlib**：数值计算和数据可视化
- **Pandas**：数据处理

### 项目架构

项目采用模块化设计，主要包含以下核心模块：

#### 1. 核心模型层 (`models/`)
- **gNB_model.py**：基站模型，负责管理用户和仿真流程
- **user_model.py**：用户模型，处理用户的信道状态和链路更新
- **channel_model.py**：信道模型，实现 Rayleigh 信道和自相关模型
- **link_adaptation.py**：链路自适应模块，支持查表法和 DNN 两种策略

#### 2. 仿真层 (`simulations/`)
- **simulation.py**：仿真主控逻辑
- **results.py**：结果收集、计算和可视化

#### 3. 深度学习层 (`DL/`)
- **training.py**：DNN 模型训练脚本
- **train_wrapper.py**：模型封装和推理接口
- **data_collector.py**：训练数据收集
- **Templates.py**：模型模板定义

#### 4. 指标层 (`metrics/`)
- **bler.py**：误块率（BLER）计算
- **delay.py**：延迟计算
- **throughput.py**：吞吐量计算

#### 5. 工具层 (`utils/`)
- **snr_to_cqi.py**：SNR 到 CQI 的映射
- **cqi_to_mcs.py**：CQI 到 MCS 的映射
- **bler_estimation.py**：BLER 估计（基于 Sigmoid 函数）
- **mapping.py**：MCS 索引映射表
- **ai_get_mcs_index.py**：AI 模型推理接口
- **generate_save_path.py**：生成保存路径

#### 6. 配置层 (`config/`)
- **DefaultConfig.py**：默认配置定义（使用 dataclass）
- **update_config.py**：配置更新工具

### 仿真流程

1. **初始化阶段**：
   - 加载配置参数（用户数量、带宽、信道类型等）
   - 初始化基站和用户
   - 生成初始 SNR 序列（考虑阴影衰落）

2. **仿真运行**：
   - 按照配置的时间步长（TTI）进行迭代
   - 每个时间步更新所有用户的信道状态
   - 根据选择的策略（查表法或 DNN）选择最优 MCS
   - 计算性能指标（吞吐量、BLER、延迟）

3. **结果输出**：
   - 收集和统计数据
   - 生成可视化图表（SNR 分布、吞吐量分布、CQI 分布等）
   - 保存结果用于后续分析或模型训练

### 链路自适应策略

#### 1. 查表法（Table Lookup）
- 基于 3GPP 标准的 CQI 到 MCS 映射表
- 通过 SNR → CQI → MCS 的映射关系选择 MCS
- 简单、快速，但可能不是最优解

#### 2. 深度学习（DNN）
- 使用神经网络直接从 SNR 预测最优 MCS
- 模型结构：
  - 输入：归一化的 SNR
  - 隐藏层：64 → 128 神经元（带 ReLU 和 BatchNorm）
  - 输出：29 个 MCS 类别的概率分布
- 支持两种模式：
  - **Lite**：轻量化模型
  - **Complex**：复杂模型
- 模型文件命名格式：`{timestamp}_{model_name}_{mode}.pth`

## 构建和运行

### 环境配置

项目使用 Conda 管理依赖环境：

```bash
# 创建并激活环境
conda create --name sionna-main --file environment.yml
conda activate sionna-main
```

主要依赖：
- Python 3.11.11
- Sionna 0.19.1
- TensorFlow 2.15.1
- PyTorch（通过 pip 安装）
- NumPy, SciPy, Matplotlib, Pandas

### 运行仿真

```bash
# 运行主仿真程序
python main.py
```

### 训练 DNN 模型

```bash
# 进入 DL 目录
cd DL

# 运行训练脚本
python training.py
```

训练脚本会：
1. 加载仿真数据（来自查表法生成的结果）
2. 构建 SNR→MCS 预测模型
3. 训练 100 个 epoch
4. 评估模型准确率
5. 保存模型参数到 `DL/results/` 目录

### 运行测试

```bash
# 运行测试脚本
python test.py
```

### 修改仿真参数

在 `main.py` 中调用 `update_config()` 函数修改配置：

```python
update_config(
    CONFIG,
    phy_layer_bandwidth=10e9,  # 带宽（Hz）
    simulation__num_users=100000000,  # 用户数
    simulation__tti_length=1,  # 时间步长数
    link_adaptation__strategy="查表",  # 或 'DNN'
    channel__ar_model={"alpha": 0.9, "sigma_ar": 0.1},  # 信道参数
    ai__data_mode='Complex',  # 'Complex' 或 'Lite'
)
```

### 配置说明

关键配置参数（在 `config/DefaultConfig.py` 中）：

- **仿真配置**：
  - `num_users`：用户数量
  - `tti_length`：仿真时间步长
  - `save_info`：是否保存结果
  - `save_path`：结果保存路径

- **物理层配置**：
  - `bandwidth`：系统带宽（默认 10GHz）
  - `fft_size`：FFT 大小
  - `rb_bandwidth`：资源块带宽（180kHz）

- **信道配置**：
  - `type`：信道类型（Rayleigh）
  - `snr`：SNR 范围和阴影衰落参数
  - `ar_model`：自相关模型参数（alpha, sigma_ar）

- **链路自适应配置**：
  - `strategy`：策略选择（"查表" 或 "DNN"）
  - `bler_target`：目标 BLER（默认 0.1）

- **用户配置**：
  - `iot_params`：IoT 用户参数（低速场景）
  - `citycar_params`：车载用户参数（高速场景）

- **AI 配置**：
  - `model_name`：模型文件名
  - `data_mode`：数据模式（"Lite" 或 "Complex"）
  - `pth_time`：模型训练时间戳

## 开发约定

### 代码风格

- 使用中文注释和文档字符串
- 函数和类命名采用驼峰命名法（PascalCase）
- 变量命名采用下划线命名法（snake_case）
- 每个主要模块都有详细的职责说明注释

### 文件组织

- 入口文件：`main.py`
- 测试文件：`test.py`
- 每个模块都有对应的 `__init__.py`（部分模块可能缺失）
- 结果文件按时间戳保存在 `results/` 目录下

### 数据文件格式

- 模型参数：`.pth`（PyTorch 格式）
- 仿真数据：`.npy`（NumPy 格式）
- 可视化图表：`.svg`（矢量图格式）

### 版本控制

- 使用 Git 进行版本控制
- 主分支：`master`
- 提交信息使用中文

### 工作目录处理

代码中多处使用 `os.chdir()` 将工作目录设置为项目根目录或特定子目录，确保相对路径正确。在开发和调试时需要注意当前工作目录的变化。

### 结果保存

仿真结果会根据时间戳自动创建目录，格式为：
```
results/YYYYMMDD_HH_{strategy}_{mode}/
```

保存的内容包括：
- SNR 数据：`{mode}_final_snr_list.npy`
- MCS 数据：`{mode}_mcs_index.npy`
- 可视化图表：SVG 格式

## 常见任务

### 1. 运行查表法仿真

在 `main.py` 中设置：
```python
link_adaptation__strategy="查表"
ai__data_mode='Lite'  # 或 'Complex'
```

### 2. 运行 DNN 模型验证

在 `main.py` 中设置：
```python
link_adaptation__strategy="DNN"
ai__pth_time="20250330_01-22"  # 指定模型时间戳
ai__data_mode='Lite'  # 或 'Complex'
```

### 3. 训练新的 DNN 模型

1. 先运行查表法仿真生成训练数据
2. 修改 `DL/training.py` 中的 `dir` 参数指向仿真数据目录
3. 运行 `python DL/training.py`
4. 获取模型时间戳并在 `main.py` 中引用

### 4. 分析仿真结果

结果保存在 `results/` 目录下，可以通过 `simulations/results.py` 中的可视化函数查看：
- SNR 分布直方图
- 吞吐量分布
- CQI 分布
- BLER 分析
- MCS 分布
- 延迟分布

## 注意事项

1. **内存使用**：当用户数量很大时（如 100,000,000），需要注意内存占用
2. **GPU 支持**：深度学习训练会自动检测并使用 GPU（如果可用）
3. **路径问题**：代码中使用相对路径，需要确保工作目录正确
4. **模型加载**：使用 DNN 策略时，确保模型文件存在于指定路径
5. **数据依赖**：训练 DNN 模型需要先运行查表法仿真生成训练数据

## 扩展和定制

### 添加新的链路自适应策略

在 `models/link_adaptation.py` 中的 `LinkAdaptation` 类中添加新的策略分支：

```python
elif self.strategy == '新策略':
    # 实现新的 MCS 选择逻辑
    pass
```

### 修改信道模型

在 `models/channel_model.py` 中修改信道生成逻辑，支持其他信道类型（如 Rician、Nakagami 等）。

### 添加新的性能指标

在 `metrics/` 目录下创建新的指标计算模块，并在 `simulations/results.py` 中集成。

### 调整模型结构

在 `DL/training.py` 中修改 `SNRMCSModel` 类的网络结构（层数、神经元数量、激活函数等）。

## 项目状态

- 当前分支：`master`
- 最近提交：文件命名规范化、精简文件结构
- 工作目录状态：干净（无未提交更改）
- 远程仓库：https://github.com/Wallfacerdl/Adaptive-Modulation-and-Coding.git

## 相关资源

- Sionna 官方文档：https://nvlabs.github.io/sionna/
- 3GPP 规范：LTE 和 NR 标准文档
- 深度学习教程：TensorFlow 和 PyTorch 官方文档
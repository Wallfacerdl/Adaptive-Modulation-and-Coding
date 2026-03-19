# Adaptive Modulation and Coding (AMC) Link Adaptation Simulation

## 1. 项目简介
本项目是一个面向无线通信链路自适应（Link Adaptation）的仿真系统，目标是在时变信道中动态选择调制与编码方案（MCS, Modulation and Coding Scheme），在满足误块率（BLER）约束的前提下尽可能提升吞吐量。

项目同时支持两类链路自适应策略：
- 基于规则/查表的 SNR -> CQI -> MCS 策略
- 基于深度学习的 SNR -> MCS 策略（DNN）

系统设计兼顾通信专业可解释性与工程可扩展性，支持参数扫描、结果可视化、测试回归和 CI 校验。

---

## 2. 通信专业背景

### 2.1 链路自适应问题
在移动通信系统（LTE/NR）中，发射端需要根据当前信道质量选择合适的 MCS：
- MCS 过高：BLER 上升，重传增加，时延恶化
- MCS 过低：频谱效率浪费，吞吐量下降

因此实际系统通常围绕目标 BLER（例如 10%）进行外环调节（OLLA, Outer Loop Link Adaptation）。

### 2.2 本项目建模要点
- 信道：采用 Rayleigh 场景下的 SNR 时变序列（含自相关）
- 质量映射：SNR -> CQI -> MCS（查表策略）
- 误块率估计：基于 MCS 参数化曲线进行 BLER 近似
- 外环调节：围绕目标 BLER 进行 MCS 上/下调

该建模方法可用于算法验证、参数对比和策略行为分析。

---

## 3. 核心能力

### 3.1 双策略链路自适应
- Table Lookup：通过 CQI 到 MCS 映射进行选择，具备可解释性
- DNN：通过学习模型预测 MCS，减少手工规则依赖

### 3.2 OLLA 可配置化
OLLA 不再硬编码，阈值可在配置中直接定义：
- table.medium_bler_upper
- table.low_bler_lower
- table.severe_bler_upper
- dnn.soft_cap

### 3.3 参数扫描能力
已提供 OLLA 扫参脚本，可批量运行不同参数组合并导出对比结果：
- summary.csv
- summary.json

### 3.4 工程可维护性
项目已重构为模式化结构：
- Strategy：MCS 选择策略解耦
- Factory：策略与 OLLA 实例创建统一管理
- Template Method：用户链路更新流程模板化
- Facade：仿真主流程封装

---

## 4. 项目结构

```text
Adaptive-Modulation-and-Coding/
├── main.py                         # 仿真入口
├── config/
│   ├── DefaultConfig.py            # 全局配置
│   ├── update_config.py            # 配置更新工具
│   ├── config_validator.py         # 配置合法性校验
│   ├── strategy.py                 # 策略枚举与归一化
│   └── paths.py                    # 项目路径上下文
├── models/
│   ├── gNB_model.py                # 基站与用户组织
│   ├── user_model.py               # 用户链路状态与更新
│   ├── channel_model.py            # 信道/SNR 生成
│   ├── link_adaptation.py          # 链路自适应门面
│   ├── mcs_selection_strategies.py # MCS 策略实现
│   ├── olla_policy.py              # OLLA 策略实现
│   ├── factory.py                  # 策略工厂
│   └── link_update_template.py     # 链路更新模板
├── simulations/
│   ├── simulation.py               # 仿真运行入口包装
│   ├── facade.py                   # 仿真编排门面
│   └── results.py                  # 统计与可视化
├── experiments/
│   └── olla_sweep.py               # OLLA 参数扫描
├── tests/
│   ├── test_olla_policy.py         # OLLA 单测
│   └── test_link_adaptation_integration.py
├── scripts/
│   └── run_ci_tests.sh             # 最小 CI 测试入口
└── .github/workflows/python-tests.yml
```

---

## 5. 运行环境

建议使用 Conda 环境（示例环境名 `com_venv`）。

### 5.1 典型依赖
- Python 3.11+
- NumPy / SciPy / Matplotlib / Pandas
- TensorFlow / PyTorch（用于 DNN 训练与推理）
- Sionna（如需物理层扩展实验）

### 5.2 环境准备（示例）
```bash
conda env create -f environment.yml
conda activate com_venv
```

---

## 6. 快速开始

### 6.1 运行主仿真
```bash
python main.py
```

### 6.2 运行 OLLA 扫参
```bash
python experiments/olla_sweep.py
```
运行后会在 `results/olla_sweep_<timestamp>/` 下生成汇总文件。

### 6.3 运行最小测试集
```bash
./scripts/run_ci_tests.sh
```
或：
```bash
python -m unittest tests/test_olla_policy.py tests/test_link_adaptation_integration.py
```

---

## 7. 链路自适应流程说明

### 7.1 单个 TTI 更新流程（用户侧）
1. 更新信道状态（SNR）
2. 由策略得到初始 MCS
3. 估计 BLER
4. 执行 OLLA 调节 MCS
5. 记录时域历史与性能指标

### 7.2 查表策略流程
SNR -> CQI -> 初始 MCS -> OLLA 调节 -> 最终 MCS

### 7.3 DNN 策略流程
SNR -> DNN 预测初始 MCS -> 保守 OLLA 修正（可选） -> 最终 MCS

---

## 8. 结果指标与输出

系统支持并输出以下核心指标：
- 平均 BLER
- 理论吞吐量 / 仿真吞吐量 / 时域平均吞吐量
- 平均时延
- MCS、CQI、SNR 分布

结果输出位置：
- 常规仿真：`results/<timestamp>_<strategy>_<mode>/`
- 扫参实验：`results/olla_sweep_<timestamp>/`

---

## 9. 参数扫描建议

在 `experiments/olla_sweep.py` 中可修改：
- CASES：参数组合列表
- num_users：用户规模
- tti_length：仿真长度

建议先小规模快速筛选，再在候选参数上放大规模复验。

---

## 10. 设计与实现亮点

- 配置校验：仿真前验证关键参数范围，避免无效实验
- 路径上下文统一：避免依赖 `os.chdir` 的全局副作用
- 策略可插拔：新增策略时无需修改主流程
- 跨平台路径：避免 Windows/Linux 分隔符兼容问题

---

## 11. 注意事项

1. 若使用 DNN 策略，请确认模型文件存在于 `DL/results/`。
2. 当用户规模很大时，建议关闭可视化以减少开销。
3. 参数扫描会多次运行仿真，建议优先用中小规模参数探索。

---

## 12. 后续扩展方向

- 引入更精细的链路层重传模型（HARQ）
- 支持更多信道模型（Rician、Nakagami）
- 增加多目标优化（吞吐量、时延、可靠性）
- 扫参脚本升级为网格搜索并自动输出 Top-N 方案

---

## 13. 致谢
本项目面向链路自适应算法研究与工程验证，欢迎在此基础上继续扩展通信场景与智能策略。
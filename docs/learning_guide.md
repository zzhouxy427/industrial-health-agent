# Industrial Health Agent 学习路线

这份文档用于按步骤理解项目，而不是只运行项目。建议每完成一个阶段，就亲自运行命令、阅读对应代码，并回答阶段末尾的问题。

## 学习方法

每个阶段都按下面顺序进行：

1. 先运行命令，观察输入和输出；
2. 再阅读对应源文件；
3. 画出数据流或写下自己的理解；
4. 修改一个小地方并重新运行；
5. 运行测试，确认没有破坏已有行为。

项目根目录：

```powershell
cd E:\agent-project
\.venv\Scripts\Activate.ps1
```

---

## 第 1 阶段：理解项目目标

### 要回答的问题

- 什么是 RUL（Remaining Useful Life，剩余寿命）？
- 为什么不能只输出一个预测数字？
- 为什么需要风险等级、预测区间和人工复核？
- Agent 在这个项目中做的是自动控制，还是辅助诊断？

### 建议阅读

- `README.md`
- `docs/architecture.md`
- `docs/model_card.md`
- `docs/limitations.md`

### 你应该学会

理解项目的真实定位：这是基于仿真数据的工业健康诊断研究型原型，不是真实设备控制系统。

---

## 第 2 阶段：理解数据

### 运行

```powershell
python src\inspect_data.py
python src\plot_sensors.py
```

### 阅读

- `src/inspect_data.py`
- `src/prepare_data.py`
- `docs/engine_1_sensors.png`

### 重点概念

- 一行数据代表发动机在某个周期的观测；
- `unit_number` 表示发动机编号；
- `cycle` 表示当前运行周期；
- `sensor_1` 到 `sensor_21` 是传感器特征；
- 训练集和测试集必须按发动机轨迹理解，而不是当作完全独立的普通表格行。

### 验收问题

- 一台发动机为什么有很多行？
- 为什么同一台发动机相邻周期的数据不能简单认为相互独立？

---

## 第 3 阶段：理解数据质量

### 运行

```powershell
python src\check_data_quality.py --unit 18
python -m pytest tests\test_data_quality.py -q
```

### 阅读

- `src/data_quality.py`
- `src/check_data_quality.py`
- `tests/test_data_quality.py`

### 重点概念

- 缺失值；
- 重复周期；
- 周期是否连续；
- 传感器值是否超出训练数据范围；
- 数据质量不通过时，为什么不应该直接相信模型预测。

---

## 第 4 阶段：理解 RUL 标签和数据拆分

### 阅读

- `src/prepare_data.py`
- `src/feature_config.py`
- `docs/experiment_report.md`

### 重点概念

训练数据中的 RUL 通常根据每台发动机的最大周期计算：

```text
RUL = 该发动机最大周期 - 当前周期
```

必须理解以下区别：

- 训练阶段可以使用标签；
- 在线诊断时只能使用当前和历史观测；
- 官方测试标签只能用于事后评估，不能进入运行时诊断流程。

---

## 第 5 阶段：理解预测模型

### 运行

```powershell
python src\train_baseline.py
python src\compare_models.py
```

### 阅读

- `src/train_baseline.py`
- `src/model.py`
- `src/compare_models.py`
- `docs/model_comparison.md`

### 重点概念

- 特征与标签；
- 训练集、验证集和测试集；
- Random Forest 的基本思想；
- MAE 与 RMSE 的区别；
- 为什么不能只根据一次测试集结果选择模型。

### 验收问题

- MAE 代表什么？
- RMSE 为什么会更重地惩罚大误差？
- Random Forest 为什么适合做当前原型的基线模型？

---

## 第 6 阶段：理解交叉验证和数据泄漏

### 运行

```powershell
python src\cross_validate_model.py
```

### 阅读

- `src/cross_validate_model.py`
- `docs/cross_validation.md`

### 重点概念

- `GroupKFold`；
- 按发动机分组；
- 同一条退化轨迹不能同时出现在训练和验证中；
- 单次留出结果与多折结果的区别；
- 均值和标准差如何表达模型稳定性。

这是本项目最重要的机器学习工程知识之一。

---

## 第 7 阶段：理解预测不确定性

### 阅读

- `src/prediction_uncertainty.py`
- `src/evaluate_prediction_intervals.py`
- `docs/experiment_report.md`

### 重点概念

- 点预测：模型认为最可能的 RUL；
- 预测区间：模型对不确定性的表达；
- P10 和 P90；
- Random Forest 树集合分位数；
- split conformal calibration；
- 区间覆盖率不是现实安全保证。

### 验收问题

- 为什么维护人员需要区间而不是单点？
- 为什么区间太窄和太宽都可能有问题？

---

## 第 8 阶段：理解风险队列

### 运行

```powershell
python src\build_risk_queue.py
python src\evaluate_risk_queue.py
```

### 阅读

- `src/risk_queue.py`
- `src/build_risk_queue.py`
- `src/evaluate_risk_queue.py`
- `docs/model_card.md`

### 重点概念

- `critical`：点预测低于风险阈值；
- `review`：预测区间下界触及风险阈值；
- `monitor`：暂不进入优先复核队列；
- 漏报与误报的权衡；
- 风险队列是人工决策支持，不是自动维修指令。

---

## 第 9 阶段：理解传感器趋势和数据漂移

### 阅读

- `src/analyze_features.py`
- `src/analyze_risk.py`
- `src/analyze_errors.py`
- `docs/architecture.md`

### 重点概念

- 传感器趋势可能与模型输出不一致；
- PSI 用于观察输入分布变化；
- 漂移不等于模型一定失效；
- 关键传感器持续上升时，即使模型风险较低，也应该提高人工复核优先级。

---

## 第 10 阶段：理解知识库和诊断报告

### 运行

```powershell
python src\retrieve_guidance.py
python src\generate_diagnostic_report.py --unit 18
```

### 阅读

- `src/retrieve_guidance.py`
- `src/generate_diagnostic_report.py`
- `docs/maintenance_knowledge.md`

### 重点概念

- 知识检索不是让模型自由编造建议；
- 报告必须区分预测结果、传感器证据和维护建议；
- 高风险结果必须人工复核；
- 报告不能直接作为真实设备维护指令。

---

## 第 11 阶段：理解 Agent 调用链

### 运行

```powershell
python src\agent_cli.py --unit 18
```

### 阅读顺序

1. `src/agent_cli.py`
2. `src/evaluate_last_cycle.py`
3. `src/analyze_features.py`
4. `src/retrieve_guidance.py`
5. `src/generate_diagnostic_report.py`
6. `src/export_agent_context.py`

### 你应该画出的流程

```text
用户请求指定发动机
    -> 读取当前数据
    -> 运行预测
    -> 分析传感器趋势
    -> 检索维护知识
    -> 生成结构化诊断报告
    -> 保存 Markdown 和 JSON 上下文
```

这里的 Agent 本质上是一个有明确工具调用顺序、数据边界和输出约束的诊断工作流。

---

## 第 12 阶段：理解 LLM 安全校验

### 阅读

- `src/llm_agent.py`
- `src/validate_llm_output.py`
- `docs/diagnostic_prompt.md`

### 重点概念

- API Key 必须通过 `.env` 读取，不能写入代码或 Git；
- LLM 只能使用结构化上下文中的数值；
- 输出必须包含风险、趋势、维护建议和人工复核说明；
- 自动停机、自动维修等危险命令必须被拒绝；
- LLM 是解释器，不是控制器。

### 运行

```powershell
python src\validate_llm_output.py
```

---

## 第 13 阶段：理解 Dashboard

### 运行

```powershell
streamlit run src\dashboard.py
```

浏览器打开 `http://localhost:8501`。

### 阅读

- `src/dashboard.py`
- `src/audit_log.py`
- `docs/demo_walkthrough.md`

### 重点观察

- 总体风险统计；
- 风险队列；
- 单台发动机诊断；
- 预测区间；
- 数据质量状态；
- LLM 辅助诊断；
- 审计历史记录。

---

## 第 14 阶段：理解测试和发布门禁

### 运行

```powershell
python -m pytest -q
python src\release_audit.py
```

### 阅读

- `tests/`
- `src/performance_gate.py`
- `src/risk_queue_gate.py`
- `src/model_snapshot.py`
- `src/release_audit.py`
- `docs/release_checklist.md`

### 重点概念

- 单元测试与集成测试；
- 性能门禁；
- 风险队列门禁；
- 模型版本和 SHA-256 完整性；
- 为什么模型不能只看一次指标就直接发布。

---

## 最终复习题

完成所有阶段后，应能独立回答：

1. 从用户选择发动机到生成报告，完整调用链是什么？
2. 为什么使用发动机级交叉验证？
3. 预测区间是如何构造的？
4. `critical` 和 `review` 的区别是什么？
5. 数据漂移和预测误差有什么区别？
6. LLM 在项目中可以做什么、不能做什么？
7. 如何保证模型文件没有被错误替换？
8. 当前项目为什么不能直接用于真实设备安全控制？

如果这些问题都能用自己的话回答，并能独立修改一个模块、补充一个测试，就说明已经真正理解了这个项目。

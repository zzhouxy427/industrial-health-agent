# 贡献指南

感谢你关注 Industrial Health Agent。这个项目是用于研究与学习的预测性维护原型；所有贡献都应保持可复现、可测试，并遵守“人工复核优先、不得自动执行安全关键操作”的边界。

## 开始前

1. Fork 仓库并从 `main` 创建描述明确的分支；
2. 使用 Python 3.10+ 创建虚拟环境；
3. 安装依赖并运行现有测试：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
```

## 提交改动的要求

- 一个 Pull Request 只聚焦一个问题；
- 新增或修改诊断规则、数据处理、风险排序、LLM 安全检查时，应同步增加或修改测试；
- 在提交前运行：

```powershell
python -m compileall -q src tests
python -m pytest -q
git diff --check
```

- 不要提交 `data/raw/`、`data/processed/`、`artifacts/`、`.venv/` 或 `.env`；
- 不要提交 API Key、访问令牌、真实设备数据或可识别的运维记录。

## 诊断与安全边界

欢迎改进预测、可解释性、数据质量、漂移监控、审计与可视化，但请遵守以下原则：

- 风险队列用于安排人工复核，不等于自动维修、停机或安全关键控制；
- LLM 只能总结已有的结构化证据，不能虚构传感器值、修改模型数值或宣称故障一定发生；
- 任何 LLM 输出都必须通过现有安全校验；
- 对 FD001 的实验结论不得直接外推为真实航空设备维护结论。

## Pull Request 描述建议

请在 PR 中写清楚：

1. 解决的问题与影响范围；
2. 使用的验证命令和结果；
3. 是否影响风险阈值、预测区间、数据质量或 LLM 安全边界；
4. 已知局限或后续工作。


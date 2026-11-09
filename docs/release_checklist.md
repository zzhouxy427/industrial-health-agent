# 发布前检查清单

本清单用于在推送重要版本、展示项目或申请实习前，快速确认项目处于可运行、可复现、且不泄露密钥的状态。

## 1. 本地环境与依赖

- [ ] 已位于项目根目录：`E:\agent-project`
- [ ] 虚拟环境已激活：`\.venv\Scripts\Activate.ps1`
- [ ] 依赖可以安装：`python -m pip install -r requirements.txt`
- [ ] 原始 FD001 文件位于 `data/raw/`，但未被 Git 跟踪。

## 2. 自动化验证

每次发布前至少运行：

```powershell
python -m pytest -q
python -m compileall -q src tests
git diff --check
```

预期：测试全部通过、无 Python 编译错误、无空白格式错误。

如需完整复现实验产物，执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_full_pipeline.ps1
```

## 3. 结果与决策边界

- [ ] 官方测试集、交叉验证和预测区间覆盖率均已在 README 与实验报告中如实记录。
- [ ] 已检查 `python src\performance_gate.py` 通过，且模型卡中的版本、指标和门限与当前结果一致。
- [ ] 风险队列区分 `critical`、`review`、`monitor`，且说明其用途是排序人工复核，不是自动维护决策。
- [ ] 已运行 `python src\evaluate_risk_queue.py`，并确认离线队列召回/误报权衡记录在实验报告中。
- [ ] 数据质量、输入漂移和传感器趋势提示仍会写入诊断报告。
- [ ] README、仪表盘与报告中保留“仅用于研究与学习”的安全边界。

## 4. 密钥与敏感信息

执行：

```powershell
git status --short
git ls-files .env data/raw artifacts
```

预期：`.env`、原始数据和运行产物不应出现在 Git 跟踪结果中。

- [ ] `.env` 只保留在本机；仓库只提交 `.env.example`。
- [ ] 截图、终端记录和 GitHub 提交中不含 API Key。
- [ ] 若密钥曾意外展示，已在服务商控制台撤销并创建新密钥。

## 5. 仪表盘手工冒烟测试

```powershell
streamlit run src\dashboard.py
```

在浏览器检查：

- [ ] 首页显示批次设备数、`critical` / `review` 数量和输入偏移提示。
- [ ] 首页显示模型版本、官方 MAE/RMSE 与性能门禁状态；若没有评估产物则明确提示“未评估”。
- [ ] 展开人工复核队列后，能看到点预测、P10/P90、优先级和复核原因。
- [ ] 选择发动机 `34`，能看到高风险示例及其诊断报告。
- [ ] 选择发动机 `18`，能看到低风险但趋势复核的示例。
- [ ] 若配置 LLM，输出通过安全校验；未配置时页面只提示配置，不报错。
- [ ] 诊断审计记录会新增一条，不写入密钥。

## 6. Git 与 GitHub

```powershell
git status --short --branch
git log -1 --oneline
git push
```

- [ ] 工作区干净，分支为 `main` 并已跟踪 `origin/main`。
- [ ] GitHub Actions 的 CI 为绿色。
- [ ] README 首页可见项目简介、关键结果、架构图、复现命令、演示脚本和局限性。
- [ ] `docs/model_card.md` 已说明模型用途、禁用用途、数据边界、指标、不确定性与变更控制。
- [ ] GitHub 页面不展示本地 `artifacts/`、原始数据或 `.env`。

## 7. 展示材料

展示或面试前准备：

1. 使用 [3 分钟演示脚本](demo_walkthrough.md) 演练一次；
2. 准备一张首页风险总览截图和一张高风险设备诊断截图；
3. 准备解释三项关键指标：官方测试误差、发动机级交叉验证、经验预测区间覆盖率；
4. 能说明模型局限性，以及为什么系统坚持“人工复核而非自动控制”。


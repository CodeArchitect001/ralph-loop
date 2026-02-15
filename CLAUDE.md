# 项目记忆 - Ralph Loop 实验

## 实验目的

对比两种 AI 辅助开发模式的效率和效果：

| 方法 | 描述 |
|------|------|
| **方法 A (Bash 版)** | 通过 shell 脚本循环调用 Claude Code，每次处理一个 story |
| **方法 B (官方插件版)** | 使用 `/ralph-loop` 命令 |

## 实验流程

### 方法 A: Bash 版

```bash
cd ~/ralph-log-analyzer
./run_bash_experiment.sh
```

实验脚本会：
1. 读取 `.ralph/stories.json` 找到第一个未完成的 story
2. 调用 `cat PROMPT.md | claude code` 处理
3. 循环最多 25 次
4. 记录日志到 `experiment_a.log`

### 方法 B: 官方插件版

```bash
/ralph-loop "开发 Log Stream Analyzer" \
  --completion-promise "COMPLETE" \
  --max-iterations 25 \
  --no-auto-approve
```

## 观察重点

- Ralph 第几轮开始理解任务结构？
- 如何处理损坏的 JSON 行（跳过还是崩溃）？
- 有没有陷入"修复 A 导致 B 坏"的循环？
- 完成速度哪个快？
- 代码质量差异
- 人工干预次数

## 当前状态

⚠️ **注意**: 代码已被直接实现，跳过了实验循环过程。

如需重新进行实验：
```bash
# 重置状态
> src/parser.py src/analyzer.py src/reporter.py src/cli.py
> tests/test_parser.py tests/test_analyzer.py
> .ralph/progress.txt

# 修改 stories.json 将所有 passes 改为 false

# 运行实验
./run_bash_experiment.sh
```

## 成功标准

1. CLI 可运行：`python -m src.cli --input tests/data/raw_logs.jsonl --output report.html`
2. 测试通过：`pytest tests/ -v`
3. 代码质量：`pylint src/ --fail-under=8.0`
4. 对比报告：记录两种方法的迭代次数、卡住点、体验差异

## 文件说明

| 文件 | 作用 |
|------|------|
| `docs/1.md` | 完整实验设计文档 |
| `.ralph/stories.json` | 任务清单（5 个 stories） |
| `.ralph/progress.txt` | 进度记录 |
| `PROMPT.md` | 开发指令模板 |
| `run_bash_experiment.sh` | Bash 版实验脚本 |
| `experiment_a.log` | Bash 版实验日志 |

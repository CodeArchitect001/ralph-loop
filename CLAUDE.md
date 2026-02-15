# 项目记忆 - Ralph Loop 实验

## 核心思想

**Ralph Loop 的本质**：每次启动 Claude Code 都是**全新会话**，无上下文记忆。

```
启动 → 完成 Story 1 → 退出 → 启动新窗口 → 完成 Story 2 → 退出 → ...
```

每次会话需要：
1. 读取 `.ralph/stories.json` 找到下一个任务
2. 读取 `.ralph/progress.txt` 了解之前做了什么
3. 从零开始理解项目状态

## 实验目的

对比两种 AI 辅助开发模式的效率和效果：

| 方法 | 描述 |
|------|------|
| **方法 A (Bash 版)** | shell 脚本循环启动独立的 Claude Code 会话 |
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
| `reset_experiment.sh` | 一键重置脚本 |
| `experiment_a.log` | Bash 版实验日志 |

## 踩坑记录

### 坑 1: Claude 一次性完成所有任务

**问题**: Claude 在一个会话里循环处理所有 stories，而不是处理完一个就退出。

**原因**: PROMPT.md 里写了"如果还有未完成的 story，继续下一轮"。

**解决**: 修改 PROMPT.md，明确要求完成 1 个 story 后立即停止并输出 `<promise>DONE</promise>`。

```diff
- 如果还有 `passes: false` 的 story，继续下一轮
+ 完成 1 个 story 后，**立即停止**，输出：`<promise>DONE</promise>`
+ **不要继续处理下一个 story**
```

### 坑 2: Claude 完成任务后不退出

**问题**: Claude 完成任务后不自动退出，一直在等待。

**原因**: 默认是交互模式，会等待用户输入。

**解决**: 使用 `--print` 非交互模式。

```bash
cat PROMPT.md | claude --print
```

### 坑 3: 非交互模式没有写入权限

**问题**: 报错 "需要授权写入权限"，但非交互模式无法弹出权限请求。

**原因**: 非交互模式下无法请求用户授权。

**解决**: 使用 `--dangerously-skip-permissions` 跳过权限检查。

```bash
cat PROMPT.md | claude --print --dangerously-skip-permissions
```

### 最终正确的调用方式

```bash
cat PROMPT.md | claude --print --dangerously-skip-permissions
```

| 参数 | 作用 |
|------|------|
| `--print` | 非交互模式，输出后自动退出 |
| `--dangerously-skip-permissions` | 跳过权限检查，无需人工授权 |

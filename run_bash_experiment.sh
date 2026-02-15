#!/bin/bash
# Bash 版 Ralph Loop 实验脚本（正确版）
#
# 核心思想：每次启动 Claude Code 都是全新会话
# - 无上下文记忆
# - 需要重新读取 stories.json 和 progress.txt
# - 模拟真实的迭代开发场景

set -e

PROJECT_DIR=~/ralph-log-analyzer
cd "$PROJECT_DIR"

# 记录开始时间
echo "============================================" | tee experiment_a.log
echo "Bash 版 Ralph Loop 实验" | tee -a experiment_a.log
echo "开始时间: $(date)" | tee -a experiment_a.log
echo "============================================" | tee -a experiment_a.log
echo "" | tee -a experiment_a.log

counter=0
max=25

while [ $counter -lt $max ]; do
  # 检查剩余未完成的 stories
  remaining=$(python3 -c "
import json
with open('.ralph/stories.json') as f:
    stories = json.load(f)['stories']
print(sum(1 for s in stories if not s['passes']))
" 2>/dev/null || echo "0")

  if [ "$remaining" = "0" ]; then
    echo "" | tee -a experiment_a.log
    echo "============================================" | tee -a experiment_a.log
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 所有 Stories 已完成!" | tee -a experiment_a.log
    echo "============================================" | tee -a experiment_a.log
    break
  fi

  # 获取当前 story 信息
  current_story=$(python3 -c "
import json
with open('.ralph/stories.json') as f:
    stories = json.load(f)['stories']
for s in stories:
    if not s['passes']:
        print(f\"Story {s['id']}: {s['task'][:30]}...\")
        break
" 2>/dev/null)

  echo "" | tee -a experiment_a.log
  echo "--------------------------------------------" | tee -a experiment_a.log
  echo "[$(date '+%H:%M:%S')] 第 $((counter+1)) 次启动 Claude Code" | tee -a experiment_a.log
  echo "  剩余 stories: $remaining" | tee -a experiment_a.log
  echo "  当前任务: $current_story" | tee -a experiment_a.log
  echo "--------------------------------------------" | tee -a experiment_a.log

  # 记录启动前的代码行数
  lines_before=$(wc -l src/*.py 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
  echo "[启动前] 代码行数: $lines_before" | tee -a experiment_a.log

  # 启动新的 Claude Code 会话
  # 使用 --print 非交互模式，--dangerously-skip-permissions 跳过权限检查
  # 关键：每次都是全新会话，无上下文记忆
  cat PROMPT.md | claude --print --dangerously-skip-permissions

  # 记录结束后的代码行数
  lines_after=$(wc -l src/*.py 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
  echo "[结束] 代码行数: $lines_after (变化: +$((lines_after - lines_before)))" | tee -a experiment_a.log

  ((counter++))

  # 如果还有未完成的任务，等待后继续
  if [ "$remaining" -gt 1 ]; then
    echo "[$(date '+%H:%M:%S')] 等待 10 秒后启动下一个会话..." | tee -a experiment_a.log
    sleep 10
  fi
done

# 记录结束信息
echo "" | tee -a experiment_a.log
echo "============================================" | tee -a experiment_a.log
echo "实验结束" | tee -a experiment_a.log
echo "============================================" | tee -a experiment_a.log
echo "结束时间: $(date)" | tee -a experiment_a.log
echo "总启动次数: $counter" | tee -a experiment_a.log
echo "" | tee -a experiment_a.log
echo "最终代码统计:" | tee -a experiment_a.log
wc -l src/*.py tests/*.py | tee -a experiment_a.log
echo "" | tee -a experiment_a.log
echo "Progress 记录:" | tee -a experiment_a.log
cat .ralph/progress.txt | tee -a experiment_a.log
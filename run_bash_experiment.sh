#!/bin/bash
# Bash 版 Ralph Loop 实验脚本

cd ~/ralph-log-analyzer

# 记录开始时间
echo "=== Bash 版 Ralph Loop 实验 ===" | tee experiment_a.log
echo "开始时间: $(date)" | tee -a experiment_a.log

counter=0
max=25

while [ $counter -lt $max ]; do
  echo "[$(date '+%H:%M:%S')] === Iteration $((counter+1))/$max ===" | tee -a experiment_a.log

  # 读取当前 story 状态
  current_story=$(python3 -c "
import json
with open('.ralph/stories.json') as f:
    stories = json.load(f)['stories']
for s in stories:
    if not s['passes']:
        print(s['id'])
        break
" 2>/dev/null)

  if [ -z "$current_story" ]; then
    echo "[$(date '+%H:%M:%S')] 所有 Stories 已完成!" | tee -a experiment_a.log
    break
  fi

  echo "[$(date '+%H:%M:%S')] 当前 Story: $current_story" | tee -a experiment_a.log

  # 执行 Claude Code 处理当前 story
  cat PROMPT.md | claude code

  ((counter++))
  echo "[$(date '+%H:%M:%S')] Sleeping 15s..." | tee -a experiment_a.log
  sleep 15
done

# 记录结束信息
echo "结束时间: $(date)" | tee -a experiment_a.log
echo "总迭代次数: $counter" | tee -a experiment_a.log
echo "最终代码行数:" | tee -a experiment_a.log
wc -l src/*.py | tee -a experiment_a.log

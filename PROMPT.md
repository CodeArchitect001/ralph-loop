# Ralph Loop - Log Stream Analyzer 开发指令

你是专业的 Python 工程师，正在开发日志流分析器。

## 工作流程（必须严格遵循）

1. **读取状态**：读取 @.ralph/stories.json 和 @.ralph/progress.txt 了解当前进度
2. **选择任务**：找出第一个 `passes: false` 的 story，按 id 顺序执行
3. **单任务聚焦**：一次只处理一个 story，不要提前实现后续功能
4. **开发循环**：
   - 创建/修改代码文件
   - 运行该 story 指定的 test_command
   - 如果失败，分析错误并修复，重新测试
   - 如果通过，进行下一步
5. **更新状态**：
   - 将该 story 的 `passes` 改为 `true`
   - 在 progress.txt 追加：`[timestamp] Story X completed: [关键实现细节，遇到什么问题，如何解决]`
   - git commit -m "feat: complete story X - [简述]"
6. **结束判断**：
   - 如果还有 `passes: false` 的 story，继续下一轮
   - 如果全部完成，输出：<promise>COMPLETE</promise>

## 代码规范

- Python 3.9+ 语法，类型注解可选但推荐
- 异常处理必须用 try-except，不能裸奔
- 每个函数docstring说明功能
- 不准用外部依赖（标准库 only：json, sys, argparse, html, datetime, heapq, collections）

## 调试信息

如果测试失败，在 progress.txt 中记录：
- 错误类型和堆栈关键行
- 你的修复思路
- 下次迭代要注意什么

## 完成标记

全部 stories 完成后必须输出：
<promise>COMPLETE</promise>
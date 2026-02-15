#!/bin/bash
# 一键重置 Ralph Loop 实验

cd ~/ralph-log-analyzer

echo "=== 重置 Ralph Loop 实验 ==="

# 1. 清空源代码文件
> src/parser.py
> src/analyzer.py
> src/reporter.py
> src/cli.py
> src/__init__.py
echo "✓ 源代码已清空"

# 2. 清空测试文件
> tests/test_parser.py
> tests/test_analyzer.py
echo "✓ 测试文件已清空"

# 3. 清空进度文件
> .ralph/progress.txt
echo "✓ 进度已清空"

# 4. 删除生成的文件
rm -f *.html experiment_a.log test.html /tmp/test_report.html 2>/dev/null
echo "✓ 临时文件已删除"

# 5. 重置 stories.json (所有 passes = false)
cat > .ralph/stories.json << 'EOF'
{
  "project": "Log Stream Analyzer",
  "language": "Python 3.9+",
  "stories": [
    {
      "id": 1,
      "task": "实现鲁棒的 JSONL 解析器（src/parser.py）",
      "description": "读取 .jsonl 文件，跳过损坏的 JSON 行，返回结构化数据",
      "acceptance_criteria": [
        "能解析 tests/data/raw_logs.jsonl 并跳过损坏行（第3行和第8行）",
        "返回 List[Dict]，每个 Dict 包含 timestamp, level, service, latency_ms, msg",
        "提供 parse_line() 单条解析函数和 parse_file() 批量解析函数",
        "损坏行记录到 stderr，但不中断处理"
      ],
      "test_command": "python -m pytest tests/test_parser.py -v",
      "passes": false
    },
    {
      "id": 2,
      "task": "实现流式分析引擎（src/analyzer.py）",
      "description": "计算统计指标：错误率、各服务 P99 延迟、日志总数",
      "acceptance_criteria": [
        "实现 LogAnalyzer 类，支持 add_record() 逐条处理和 get_stats() 获取结果",
        "统计指标包括：total_logs, error_count, error_rate%, 各服务的 p50/p99 延迟",
        "使用 heapq 或 sorted 计算百分位数，不准用 numpy（保持轻量）",
        "处理空输入不报错"
      ],
      "test_command": "python -m pytest tests/test_analyzer.py -v",
      "passes": false
    },
    {
      "id": 3,
      "task": "实现 HTML 报告生成器（src/reporter.py）",
      "description": "生成漂亮的 HTML 监控面板，包含图表（用纯 HTML/CSS，无需 JS 库）",
      "acceptance_criteria": [
        "生成包含以下内容的 HTML：标题、统计摘要卡片（总数/错误率/P99）、服务详情表格",
        "错误率用颜色标识：<1% 绿色，1-5% 黄色，>5% 红色",
        "HTML 文件可独立打开，不依赖外部 CDN（内联样式）",
        "输出路径通过参数指定，默认 report.html"
      ],
      "test_command": "python -c \"from src.reporter import generate_report; generate_report({'total': 100}, 'test.html')\" && test -f test.html",
      "passes": false
    },
    {
      "id": 4,
      "task": "实现 CLI 接口（src/cli.py）",
      "description": "命令行入口，使用 argparse 处理参数",
      "acceptance_criteria": [
        "命令行接口：python -m src.cli --input logs.jsonl --output report.html",
        "支持 --window-size 参数（只分析最近 N 条日志，默认全部）",
        "支持 --verbose 标志，显示处理进度",
        "返回码：成功 0，文件不存在 1，解析错误 2"
      ],
      "test_command": "python -m src.cli --input tests/data/raw_logs.jsonl --output /tmp/test_report.html && test -f /tmp/test_report.html",
      "passes": false
    },
    {
      "id": 5,
      "task": "端到端集成与测试",
      "description": "完整流程验证和代码清理",
      "acceptance_criteria": [
        "运行完整流程：python -m src.cli --input tests/data/raw_logs.jsonl --output final_report.html",
        "生成的 final_report.html 能用浏览器正常打开，包含所有统计信息",
        "所有 pytest 通过，无 pylint 警告（pylint src/ 评分 > 8.0）",
        "README.md 包含使用说明和示例输出截图"
      ],
      "test_command": "pylint src/ --fail-under=8.0 && pytest tests/ -v",
      "passes": false
    }
  ]
}
EOF
echo "✓ Stories 已重置"

# 6. 显示状态
echo ""
echo "=== 重置完成 ==="
echo "源代码:    $(wc -l < src/parser.py) 行"
echo "测试文件:  $(wc -l < tests/test_parser.py) 行"
echo "Stories:   5 个未完成"
echo ""
echo "运行实验:  ./run_bash_experiment.sh"

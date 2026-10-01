# AI 数据分析助手

上传 CSV 表格，自动完成描述性统计，并调用大模型生成结构化的数据分析结论（概况、关键发现、异常趋势、可执行建议）。

## 特性
- 自动识别数值列 / 分类列，分别做均值/中位数/极差 和 频次统计
- 零重依赖：纯标准库 `csv` + `statistics`
- LLM 生成专业分析结论

## 快速开始
```bash
export LLM_API_KEY="你的Key"
python main.py sample_data/sales.csv
```

## 应用场景
- 运营/销售数据分析
- 报表自动解读
- 数据洞察探索

## License
MIT

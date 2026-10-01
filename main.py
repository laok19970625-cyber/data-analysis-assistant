"""命令行入口：分析 CSV 文件。用法: python main.py <csv路径>"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from analyzer import LLMClient, analyze, load_csv, summarize  # noqa: E402


def main():
    if len(sys.argv) < 2:
        csv_path = str(Path(__file__).parent / "sample_data" / "sales.csv")
        print(f"未指定文件，使用示例数据：{csv_path}")
    else:
        csv_path = sys.argv[1]

    data = load_csv(csv_path)
    print(f"已加载 {len(data)} 行数据\n")

    summary = summarize(data)
    print("=== 统计摘要 ===")
    for col in summary["columns"]:
        print(f"- {col['name']} ({col['type']}):", end=" ")
        if col["type"] == "numeric":
            print(f"均值={col['mean']}, 中位数={col['median']}, 范围=[{col['min']}, {col['max']}]")
        else:
            print(f"{col['unique']} 类，Top={col['top'][:3]}")
    print()

    print("=== AI 分析结论 ===")
    try:
        print(analyze(data, LLMClient()))
    except RuntimeError as e:
        print(f"[错误] {e}")


if __name__ == "__main__":
    main()

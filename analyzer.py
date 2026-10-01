"""AI 数据分析助手：读入 CSV/表格数据 -> 统计描述 -> LLM 生成分析结论。

零重依赖：用标准库 csv + statistics 计算描述性统计，再交给 LLM 解读。
"""

from __future__ import annotations

import csv
import json
import os
import statistics
import urllib.request
from typing import List


class LLMClient:
    def __init__(self, api_key=None, api_base=None, model=None):
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "")
        self.api_base = (api_base or os.environ.get("LLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4")).rstrip("/")
        self.model = model or os.environ.get("LLM_MODEL", "glm-4-flash")

    def chat(self, messages, temperature=0.3):
        if not self.api_key:
            raise RuntimeError("未配置 LLM_API_KEY，请设置环境变量后重试。")
        url = f"{self.api_base}/chat/completions"
        payload = {"model": self.model, "messages": messages, "temperature": temperature}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]


def load_csv(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def summarize(data: List[dict]) -> dict:
    """对每列做描述性统计：数值列算均值/中位数/最大最小，文本列算频次 Top。"""
    if not data:
        return {"rows": 0, "columns": []}
    columns = list(data[0].keys())
    summary = {"rows": len(data), "columns": []}
    for col in columns:
        values = [row[col] for row in data if row.get(col) not in (None, "")]
        # 尝试转数值
        numeric = []
        for v in values:
            try:
                numeric.append(float(v))
            except (ValueError, TypeError):
                numeric = None
                break
        if numeric is not None and len(numeric) > 0:
            summary["columns"].append({
                "name": col,
                "type": "numeric",
                "count": len(numeric),
                "mean": round(statistics.mean(numeric), 2),
                "median": round(statistics.median(numeric), 2),
                "min": min(numeric),
                "max": max(numeric),
                "stdev": round(statistics.stdev(numeric), 2) if len(numeric) > 1 else 0,
            })
        else:
            # 文本列：频次
            freq = {}
            for v in values:
                freq[v] = freq.get(v, 0) + 1
            top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
            summary["columns"].append({
                "name": col,
                "type": "categorical",
                "count": len(values),
                "unique": len(freq),
                "top": top,
            })
    return summary


SYSTEM_PROMPT = (
    "你是一名资深数据分析师。请基于给定的数据统计摘要，"
    "输出一份清晰的数据分析结论，包含：1) 数据概况 2) 关键发现 3) 值得关注的异常或趋势 4) 可执行的建议。"
    "用中文，条理清晰，直接给结论。"
)


def analyze(data: List[dict], llm: LLMClient) -> str:
    summary = summarize(data)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"数据统计摘要：\n{json.dumps(summary, ensure_ascii=False, indent=2)}"},
    ]
    return llm.chat(messages)

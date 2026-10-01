"""数据分析助手单元测试。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from analyzer import LLMClient, load_csv, summarize  # noqa: E402


class TestSummarize(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"月份": "1月", "销售额": "100", "地区": "华东"},
            {"月份": "2月", "销售额": "200", "地区": "华南"},
            {"月份": "3月", "销售额": "300", "地区": "华东"},
        ]

    def test_numeric_column(self):
        s = summarize(self.data)
        sales = [c for c in s["columns"] if c["name"] == "销售额"][0]
        self.assertEqual(sales["type"], "numeric")
        self.assertEqual(sales["mean"], 200.0)
        self.assertEqual(sales["min"], 100.0)
        self.assertEqual(sales["max"], 300.0)

    def test_categorical_column(self):
        s = summarize(self.data)
        region = [c for c in s["columns"] if c["name"] == "地区"][0]
        self.assertEqual(region["type"], "categorical")
        self.assertEqual(region["unique"], 2)

    def test_load_csv(self):
        path = Path(__file__).parent.parent / "sample_data" / "sales.csv"
        data = load_csv(str(path))
        self.assertEqual(len(data), 12)
        self.assertIn("销售额", data[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)

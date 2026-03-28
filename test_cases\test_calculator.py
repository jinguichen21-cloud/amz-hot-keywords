#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试涨跌幅度计算逻辑
Test Calculator Module
"""

import unittest
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


def calculate_trend(current_rank, last_rank):
    """
    根据排名变化计算涨跌幅度
    
    规则：
    - 本周排名 < 上周排名 → 上升（数字越小排名越靠前）
    - 本周排名 > 上周排名 → 下降
    - 本周排名 == 上周排名 → 持平
    - 上周排名为 0 或空 → 上升（新上榜）
    """
    if last_rank == 0 or last_rank is None:
        return "上升"  # 新上榜
    elif current_rank < last_rank:
        return "上升"
    elif current_rank > last_rank:
        return "下降"
    else:
        return "持平"


class CalculatorTests(unittest.TestCase):
    """涨跌幅度计算测试"""
    
    def test_rising_rank_2_to_1(self):
        """测试排名上升：从第 2 名到第 1 名"""
        result = calculate_trend(1, 2)
        self.assertEqual(result, "上升")
    
    def test_rising_rank_10_to_5(self):
        """测试排名上升：从第 10 名到第 5 名"""
        result = calculate_trend(5, 10)
        self.assertEqual(result, "上升")
    
    def test_falling_rank_1_to_2(self):
        """测试排名下降：从第 1 名到第 2 名"""
        result = calculate_trend(2, 1)
        self.assertEqual(result, "下降")
    
    def test_falling_rank_3_to_5(self):
        """测试排名下降：从第 3 名到第 5 名"""
        result = calculate_trend(5, 3)
        self.assertEqual(result, "下降")
    
    def test_stable_rank(self):
        """测试排名持平"""
        result = calculate_trend(5, 5)
        self.assertEqual(result, "持平")
    
    def test_new_entry_zero_last_rank(self):
        """测试新上榜：上周排名为 0"""
        result = calculate_trend(10, 0)
        self.assertEqual(result, "上升")
    
    def test_new_entry_none_last_rank(self):
        """测试新上榜：上周排名为 None"""
        result = calculate_trend(10, None)
        self.assertEqual(result, "上升")
    
    def test_edge_case_rank_1(self):
        """测试边界情况：保持第 1 名"""
        result = calculate_trend(1, 1)
        self.assertEqual(result, "持平")
    
    def test_large_rank_change(self):
        """测试大幅度排名变化"""
        result = calculate_trend(1, 100)
        self.assertEqual(result, "上升")
        
        result = calculate_trend(100, 1)
        self.assertEqual(result, "下降")


if __name__ == '__main__':
    unittest.main(verbosity=2)

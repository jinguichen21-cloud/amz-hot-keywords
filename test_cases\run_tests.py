#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search Scraper 自动化测试运行器
Test Runner for Hot Search Scraper Skill Package

使用方法:
    python3 run_tests.py              # 运行所有测试
    python3 run_tests.py --verbose    # 详细输出
    python3 run_tests.py calculator   # 只运行计算测试
    python3 run_tests.py config       # 只运行配置测试
"""

import unittest
import sys
import os
import argparse
from datetime import datetime

# Add scripts directory to path
scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, scripts_dir)


def create_test_suite(test_modules=None):
    """创建测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Default test modules
    if test_modules is None:
        test_modules = ['test_calculator', 'test_config']
    
    # Load tests from specified modules
    for module_name in test_modules:
        try:
            # Import from current directory
            spec = __import__(module_name)
            tests = loader.loadTestsFromModule(spec)
            suite.addTests(tests)
            print(f"✓ 已加载测试模块：{module_name}")
        except ImportError as e:
            print(f"✗ 无法加载测试模块 {module_name}: {e}")
    
    return suite


def run_tests(suite, verbosity=2):
    """运行测试并返回结果"""
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        failfast=False,
        buffer=False,
        catchbreak=False
    )
    
    print("\n" + "=" * 70)
    print("Hot Search Scraper 技能包 - 自动化测试")
    print("=" * 70)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    print(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总测试数：{result.testsRun}")
    print(f"成功：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")
    print("=" * 70)
    
    if result.failures:
        print("\n失败用例:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n错误用例:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Hot Search Scraper 技能包测试运行器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 run_tests.py                    # 运行所有测试
  python3 run_tests.py --verbose          # 详细输出
  python3 run_tests.py calculator         # 只运行计算测试
  python3 run_tests.py config             # 只运行配置测试
  python3 run_tests.py calculator config  # 运行多个指定测试
        """
    )
    
    parser.add_argument(
        'modules',
        nargs='*',
        default=None,
        help='要运行的测试模块名称 (默认：运行所有)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='静默模式，只显示摘要'
    )
    
    args = parser.parse_args()
    
    # Determine verbosity
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1
    
    # Create test suite
    suite = create_test_suite(args.modules)
    
    if suite.countTestCases() == 0:
        print("✗ 没有找到任何测试用例")
        print("\n可用的测试模块:")
        print("  - calculator: 涨跌幅度计算测试")
        print("  - config: 配置文件管理测试")
        return 1
    
    # Run tests
    result = run_tests(suite, verbosity)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())

# Hot Search Scraper 测试指南

## 目录结构

```
test_cases/
├── README.md              # 本文件
├── TEST_CASES.md          # 完整测试用例文档（70+ 测试用例）
├── run_tests.py           # 自动化测试运行器
├── test_calculator.py     # 涨跌幅度计算测试（9 个用例）
└── test_config.py         # 配置文件管理测试（6 个用例）
```

## 快速开始

### 前置条件

确保已安装所需依赖：

```bash
cd /Users/kitano/.real/workspace/hot_search_scraper
pip3 install requests beautifulsoup4 pandas fake-useragent
```

### 运行所有测试

**方法 1：使用测试运行器**

```bash
cd test_cases
python3 run_tests.py --verbose
```

**方法 2：使用 unittest 直接运行**

```bash
cd test_cases
python3 -m unittest discover -v
```

### 运行特定测试模块

**只运行计算器测试：**
```bash
python3 -m unittest test_calculator.CalculatorTests -v
```

**只运行配置测试：**
```bash
python3 -m unittest test_config.ConfigTests -v
```

### 运行单个测试用例

```bash
# 运行特定的测试方法
python3 -m unittest test_calculator.CalculatorTests.test_rising_rank_2_to_1 -v

# 运行配置加载测试
python3 -m unittest test_config.ConfigTests.test_load_existing_config -v
```

## 测试结果示例

### 成功输出

```
======================================================================
Hot Search Scraper 技能包 - 自动化测试
======================================================================
开始时间：2026-03-14 15:45:00
======================================================================

test_edge_case_rank_1 (test_calculator.CalculatorTests)
测试边界情况：保持第 1 名 ... ok
test_falling_rank_1_to_2 (test_calculator.CalculatorTests)
测试排名下降：从第 1 名到第 2 名 ... ok
...

----------------------------------------------------------------------
Ran 15 tests in 0.015s

OK
```

### 失败输出

```
======================================================================
FAIL: test_rising_rank_2_to_1 (test_calculator.CalculatorTests)
测试排名上升：从第 2 名到第 1 名
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/hot_search_scraper/test_cases/test_calculator.py", line 25, in test_rising_rank_2_to_1
    self.assertEqual(result, "上升")
AssertionError: '下降' != '上升'

----------------------------------------------------------------------
Ran 15 tests in 0.012s

FAILED (failures=1)
```

## 测试覆盖说明

### 已覆盖的测试类型

| 测试类型 | 测试文件 | 用例数 | 状态 |
|---------|---------|-------|------|
| **单元测试** | | | |
| - 涨跌幅度计算 | test_calculator.py | 9 | ✅ |
| - 配置文件管理 | test_config.py | 6 | ✅ |
| **集成测试** | | | |
| - 端到端数据流 | (手动执行) | 4 | 📝 |
| - 钉钉表格操作 | (手动执行) | 3 | 📝 |
| **边界与异常** | | | |
| - 网络异常 | (手动执行) | 3 | 📝 |
| - 数据异常 | (手动执行) | 3 | 📝 |
| **总计** | | **28+** | |

✅ = 已自动化  
📝 = 需手动执行（见 TEST_CASES.md）

### 测试覆盖率目标

- **核心逻辑**（数据抓取、计算、写入）：≥ 90%
- **错误处理分支**：≥ 80%
- **整体覆盖率**：≥ 85%

### 检查测试覆盖率

```bash
# 安装 coverage 工具
pip3 install coverage

# 运行测试并生成覆盖率报告
coverage run --source=../scripts -m unittest discover
coverage report -m
coverage html  # 生成 HTML 可视化报告

# 查看 HTML 报告
open htmlcov/index.html
```

## 手动测试用例

完整的测试用例文档包含 **70+ 个测试用例**，详见 [`TEST_CASES.md`](TEST_CASES.md)。

### 需要手动执行的测试

以下测试需要真实环境和外部服务，建议定期执行：

1. **端到端测试** (TC-E2E-001 ~ TC-E2E-004)
   - 需要访问 AMZ123 网站
   - 需要有效的钉钉表格配置
   
2. **钉钉表格操作测试** (TC-DINGTALK-001 ~ TC-DINGTALK-003)
   - 需要真实的 AI表格
   - 需要有效的 MCP 凭证

3. **网络异常测试** (TC-NETWORK-001 ~ TC-NETWORK-003)
   - 模拟断网或慢速网络环境

4. **性能测试** (TC-PERF-001 ~ TC-PERF-002)
   - 大批量数据处理
   - 快速连续执行

## 持续集成

### 在 CI/CD 中运行测试

创建 `.github/workflows/test.yml` 或类似配置：

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip3 install -r requirements.txt
        pip3 install requests beautifulsoup4 pandas fake-useragent
    
    - name: Run tests
      working-directory: hot_search_scraper/test_cases
      run: |
        python3 run_tests.py --verbose
```

### 预提交检查

在提交代码前自动运行测试：

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running tests before commit..."
cd hot_search_scraper/test_cases
python3 run_tests.py --quiet

if [ $? -eq 0 ]; then
    exit 0
else
    echo "Tests failed! Commit aborted."
    exit 1
fi
```

## 故障排查

### 常见问题

#### 1. `ModuleNotFoundError: No module named 'requests'`

**解决方案：**
```bash
pip3 install requests beautifulsoup4 pandas fake-useragent
```

#### 2. 测试失败：配置文件路径错误

**原因：** 测试修改了配置文件，但清理不彻底

**解决方案：**
```bash
# 恢复原始配置
cd ../scripts
git checkout scraper_config.json

# 或者手动删除测试备份
rm -f scraper_config.json.bak
```

#### 3. 导入错误：无法找到测试模块

**原因：** Python 路径问题

**解决方案：**
```bash
# 确保在 test_cases 目录运行
cd test_cases
python3 -m unittest discover
```

### 调试单个测试

```bash
# 使用 pdb 调试
python3 -m pdb -m unittest test_calculator.CalculatorTests.test_rising_rank_2_to_1

# 或在测试代码中添加断点
import pdb; pdb.set_trace()
```

## 测试最佳实践

1. **测试命名规范**
   - 使用描述性的测试方法名
   - 格式：`test_<场景>_<预期结果>`
   - 例如：`test_rising_rank_2_to_1`

2. **测试独立性**
   - 每个测试应该独立运行
   - 使用 `setUp()` 和 `tearDown()` 管理测试环境
   - 避免测试间的依赖关系

3. **断言清晰**
   - 使用具体的断言方法（`assertEqual`, `assertTrue`）
   - 添加有意义的错误消息

4. **边界值测试**
   - 测试最小值、最大值、空值
   - 测试特殊字符和异常情况

5. **定期回归测试**
   - 每次修改代码后运行完整测试套件
   - 发布前执行所有手动测试用例

## 贡献指南

### 添加新测试

1. 在相应的测试文件中添加测试方法
2. 遵循命名规范：`test_<功能>_<场景>`
3. 确保测试独立且可重复
4. 更新本文档的测试覆盖表格

### 报告测试问题

发现测试失败或遗漏时，请提供：

- 测试用例 ID（如 TC-CALC-001）
- 执行环境（Python 版本、操作系统）
- 完整的错误信息
- 重现步骤

## 参考资料

- [完整测试用例文档](TEST_CASES.md)
- [Python unittest 官方文档](https://docs.python.org/3/library/unittest.html)
- [测试覆盖率工具](https://coverage.readthedocs.io/)

---

**最后更新时间：** 2026-03-14  
**维护者：** 北野川

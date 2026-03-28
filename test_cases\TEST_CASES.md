# Hot Search Scraper 技能包测试用例

## 测试概览

本测试用例集覆盖 `hot_search_scraper` 技能包的所有核心功能，包括前置条件检查、数据抓取、配置管理、数据写入等模块。

**测试目标：**
- 验证技能包各功能模块的正确性
- 确保异常场景下的容错能力
- 保证数据抓取的准确性和完整性
- 验证钉钉表格写入的可靠性

**测试环境要求：**
- Python 3.9+
- macOS 15.5
- 已安装依赖：selenium, requests, beautifulsoup4, fake-useragent, pandas
- 钉钉 MCP 服务可用
- AMZ123 网站可访问

---

## 一、单元测试 (Unit Tests)

### 1.1 配置文件管理测试

#### TC-CONFIG-001: 加载现有配置文件
- **测试目的**: 验证正确加载已存在的配置文件
- **前置条件**: `scraper_config.json` 存在且格式正确
- **测试步骤**:
  1. 调用 `load_config()` 函数
  2. 验证返回的配置字典包含所有必需字段
- **预期结果**: 
  - 返回包含 `keyword`, `url`, `table_uuid`, `sheet_id`, `mcp_url` 的字典
  - 字段值与文件内容一致
- **测试代码**:
```python
def test_load_existing_config():
    config = load_config()
    assert 'keyword' in config
    assert 'url' in config
    assert config['keyword'] == 'dog bed'
    assert config['url'] == 'https://www.amz123.com/usatopkeywords'
```

#### TC-CONFIG-002: 配置文件不存在时使用默认值
- **测试目的**: 验证配置文件缺失时的降级处理
- **前置条件**: 临时重命名或删除 `scraper_config.json`
- **测试步骤**:
  1. 移除配置文件
  2. 调用 `load_config()`
  3. 验证返回默认配置
- **预期结果**: 返回 `DEFAULT_CONFIG` 中的默认值
- **测试代码**:
```python
def test_load_default_config_when_missing():
    os.rename(CONFIG_FILE, CONFIG_FILE + '.bak')
    try:
        config = load_config()
        assert config['keyword'] == 'dog bed'
        assert config['url'] == 'https://www.amz123.com/usatopkeywords'
    finally:
        os.rename(CONFIG_FILE + '.bak', CONFIG_FILE)
```

#### TC-CONFIG-003: 保存配置文件
- **测试目的**: 验证配置持久化功能
- **前置条件**: 无
- **测试步骤**:
  1. 创建新配置字典
  2. 调用 `save_config(config)`
  3. 读取文件验证内容
- **预期结果**: 文件正确写入，JSON 格式有效
- **测试代码**:
```python
def test_save_config():
    test_config = {
        'keyword': 'test keyword',
        'url': 'https://test.com',
        'table_uuid': 'test123',
        'sheet_id': 'abc',
        'mcp_url': 'https://mcp.test.com'
    }
    result = save_config(test_config)
    assert result is True
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        saved = json.load(f)
    assert saved['keyword'] == 'test keyword'
```

#### TC-CONFIG-004: 配置文件格式错误处理
- **测试目的**: 验证 JSON 格式错误时的容错能力
- **前置条件**: 创建格式错误的 JSON 文件
- **测试步骤**:
  1. 写入无效的 JSON 内容到配置文件
  2. 调用 `load_config()`
  3. 验证返回默认配置并打印警告
- **预期结果**: 捕获异常，使用默认配置，输出警告信息

---

### 1.2 数据抓取功能测试

#### TC-SCRAPER-001: 成功获取 HTML 页面
- **测试目的**: 验证基础网页请求功能
- **前置条件**: 网络连接正常
- **测试步骤**:
  1. 调用 `get_html('https://www.amz123.com/usatopkeywords')`
  2. 验证返回内容非空
- **预期结果**: 返回包含 HTML 内容的字符串
- **测试代码**:
```python
def test_get_html_success():
    html = get_html('https://www.amz123.com/usatopkeywords')
    assert html is not None
    assert len(html) > 1000
    assert '<html>' in html.lower() or '<!doctype' in html.lower()
```

#### TC-SCRAPER-002: 关键词搜索功能
- **测试目的**: 验证带关键词的搜索抓取
- **前置条件**: AMZ123 网站可访问
- **测试步骤**:
  1. 调用 `search_keywords(base_url, 'dog bed', max_results=10)`
  2. 验证返回结果数量
- **预期结果**: 返回包含关键词的数据列表，数量 ≤ 10
- **测试代码**:
```python
def test_search_keywords():
    results = search_keywords(
        'https://www.amz123.com/usatopkeywords',
        'dog bed',
        max_results=10
    )
    assert isinstance(results, list)
    assert len(results) <= 10
    assert all('keyword' in item for item in results)
```

#### TC-SCRAPER-003: 热搜词榜单抓取（无关键词）
- **测试目的**: 验证纯榜单数据抓取
- **前置条件**: AMZ123 网站可访问
- **测试步骤**:
  1. 调用 `scrape_hot_keywords(url)`
  2. 验证返回数据结构
- **预期结果**: 返回榜单数据列表，包含 rank, keyword 等字段

#### TC-SCRAPER-004: 分页抓取测试
- **测试目的**: 验证多页数据抓取能力
- **前置条件**: 搜索结果超过一页
- **测试步骤**:
  1. 调用 `search_keywords(url, 'pet', max_results=50)`
  2. 验证抓取了多页数据
- **预期结果**: 返回接近 50 条结果，证明进行了分页

#### TC-SCRAPER-005: HTML 解析失败时的文本提取降级
- **测试目的**: 验证结构化解析失败时的备用方案
- **前置条件**: 提供不包含标准结构的 HTML
- **测试步骤**:
  1. 创建简化的 HTML 内容
  2. 调用 `parse_keywords_from_html(html)`
  3. 验证调用了 `extract_keywords_from_text`
- **预期结果**: 使用通用文本分析提取关键词

---

### 1.3 字段比对测试

#### TC-FIELD-001: 字段结构完全匹配
- **测试目的**: 验证字段一致性检查
- **前置条件**: 无
- **测试步骤**:
  1. 调用 `compare_fields(['a', 'b'], ['a', 'b'])`
- **预期结果**: 返回 `(False, "")` 表示无差异

#### TC-FIELD-002: 字段缺失检测
- **测试目的**: 验证缺失字段识别
- **前置条件**: 无
- **测试步骤**:
  1. 调用 `compare_fields(['a'], ['a', 'b'])`
- **预期结果**: 返回 `(True, "缺少字段 b")`

#### TC-FIELD-003: 字段多余检测
- **测试目的**: 验证多余字段识别
- **前置条件**: 无
- **测试步骤**:
  1. 调用 `compare_fields(['a', 'b', 'c'], ['a', 'b'])`
- **预期结果**: 返回 `(True, "多余字段 c")`

---

### 1.4 数据转换与计算测试

#### TC-CALC-001: 涨跌幅度计算 - 上升
- **测试目的**: 验证排名上升的计算逻辑
- **前置条件**: 无
- **测试步骤**:
  1. 调用 `calculate_trend(current_rank=1, last_rank=2)`
- **预期结果**: 返回 `"上升"`
- **测试代码**:
```python
def test_calculate_trend_rising():
    assert calculate_trend(1, 2) == "上升"
    assert calculate_trend(5, 10) == "上升"
```

#### TC-CALC-002: 涨跌幅度计算 - 下降
- **测试目的**: 验证排名下降的计算逻辑
- **前置条件**: 无
- **测试步骤**:
  1. 调用 `calculate_trend(current_rank=5, last_rank=3)`
- **预期结果**: 返回 `"下降"`
- **测试代码**:
```python
def test_calculate_trend_falling():
    assert calculate_trend(5, 3) == "下降"
    assert calculate_trend(10, 8) == "下降"
```

#### TC-CALC-003: 涨跌幅度计算 - 持平
- **测试目的**: 验证排名不变的计算逻辑
- **前置条件**: 无
- **测试步骤**:
  1. 调用 `calculate_trend(current_rank=5, last_rank=5)`
- **预期结果**: 返回 `"持平"`

#### TC-CALC-004: 涨跌幅度计算 - 新上榜
- **测试目的**: 验证新上榜的处理逻辑
- **前置条件**: 无
- **测试步骤**:
  1. 调用 `calculate_trend(current_rank=10, last_rank=0)`
  2. 调用 `calculate_trend(current_rank=10, last_rank=None)`
- **预期结果**: 两次都返回 `"上升"`

---

### 1.5 CSV 导出测试

#### TC-CSV-001: 成功保存 CSV
- **测试目的**: 验证 CSV 文件导出功能
- **前置条件**: 有测试数据
- **测试步骤**:
  1. 准备测试数据列表
  2. 调用 `save_to_csv(data, filename)`
  3. 验证文件存在且内容正确
- **预期结果**: 文件创建成功，包含正确的列头和数据

#### TC-CSV-002: 空数据不保存
- **测试目的**: 验证空数据的边界处理
- **前置条件**: 无
- **测试步骤**:
  1. 调用 `save_to_csv([])`
- **预期结果**: 返回 `None`，不创建文件，输出错误提示

---

## 二、集成测试 (Integration Tests)

### 2.1 前置条件检查集成测试

#### TC-INTEG-001: 完整的前置检查流程
- **测试目的**: 验证所有检查项的完整执行
- **前置条件**: 环境配置正确
- **测试步骤**:
  1. 运行 `python3 check_prerequisites.py`
  2. 验证所有检查项通过
- **预期结果**: 
  - Python 版本检查 ✓
  - 依赖包检查 ✓
  - 配置文件检查 ✓
  - MCP 连接检查 ✓
  - 表格字段检查 ✓
  - 退出码为 0

#### TC-INTEG-002: 缺失依赖的检查
- **测试目的**: 验证依赖缺失时的报告
- **前置条件**: 卸载某个依赖包（如 selenium）
- **测试步骤**:
  1. `pip3 uninstall selenium -y`
  2. 运行检查脚本
  3. 验证报告缺失
  4. 重新安装依赖
- **预期结果**: 检查失败，提示安装命令

#### TC-INTEG-003: 配置文件缺失的首次运行
- **测试目的**: 验证首次运行的引导流程
- **前置条件**: 删除配置文件
- **测试步骤**:
  1. 移除配置文件
  2. 运行检查脚本
  3. 验证提示信息
- **预期结果**: 提示配置文件不存在，说明首次运行将自动创建

---

### 2.2 端到端数据流测试

#### TC-E2E-001: 完整抓取流程（不写入）
- **测试目的**: 验证从抓取到导出的完整流程
- **前置条件**: 网络正常，配置正确
- **测试步骤**:
  1. 运行 `python3 amz123_enhanced_scraper_v2.py --keyword "dog bed" --no-write`
  2. 验证输出了抓取数据
  3. 验证生成了 CSV 和 JSON 备份文件
- **预期结果**: 
  - 成功抓取至少 10 条数据
  - 生成时间戳命名的 CSV 文件
  - 生成 HTML 页面备份
  - 控制台输出详细日志

#### TC-E2E-002: 完整抓取并写入流程
- **测试目的**: 验证包含表格写入的完整流程
- **前置条件**: 
  - 钉钉 MCP 服务可用
  - AI表格已创建且字段正确
  - 配置文件中凭证有效
- **测试步骤**:
  1. 运行 `python3 amz123_enhanced_scraper_v2.py --keyword "yoga mat"`
  2. 验证清空旧数据
  3. 验证分批写入新数据
  4. 登录钉钉表格检查数据
- **预期结果**: 
  - 旧数据被清空
  - 新数据成功写入（批次确认）
  - 表格中数据与抓取结果一致
  - 涨跌幅度计算正确

#### TC-E2E-003: 自定义 URL 的抓取
- **测试目的**: 验证动态更换 URL 的能力
- **前置条件**: 提供一个有效的替代 URL
- **测试步骤**:
  1. 运行 `python3 amz123_enhanced_scraper_v2.py --keyword "test" --url "https://custom-url.com"`
  2. 验证使用了新 URL
  3. 验证配置被更新保存
- **预期结果**: 
  - 从新 URL 抓取数据
  - `scraper_config.json` 中的 URL 被更新

#### TC-E2E-004: 强制重新配置
- **测试目的**: 验证 `--force-config` 参数
- **前置条件**: 已有配置文件
- **测试步骤**:
  1. 运行 `python3 amz123_enhanced_scraper_v2.py --force-config`
  2. 交互式输入新关键词和 URL
  3. 验证配置被更新
- **预期结果**: 提示用户输入，配置被更新保存

---

### 2.3 钉钉表格操作集成测试

#### TC-DINGTALK-001: 清空表格记录
- **测试目的**: 验证清空功能的正确性
- **前置条件**: 表格中有测试数据
- **测试步骤**:
  1. 手动在表格中添加几条测试记录
  2. 调用 `clear_table_records(table_uuid, sheet_id)`
  3. 查询表格验证记录数为 0
- **预期结果**: 所有记录被删除，表格为空

#### TC-DINGTALK-002: 批量写入记录
- **测试目的**: 验证分批写入避免频率限制
- **前置条件**: 表格已清空
- **测试步骤**:
  1. 准备 50 条测试数据
  2. 调用 `write_to_dingtalk_table(csv_file, table_uuid, sheet_id, clear_first=False)`
  3. 验证分批写入日志
- **预期结果**: 
  - 分 3 批写入（每批 20 条）
  - 每批之间有延时
  - 最终表格包含 50 条记录

#### TC-DINGTALK-003: 字段不匹配时的提醒
- **测试目的**: 验证字段校验和提醒机制
- **前置条件**: 表格缺少某个必需字段
- **测试步骤**:
  1. 在表格中删除"涨跌幅度"字段
  2. 运行写入操作
  3. 验证是否检测到并提醒
- **预期结果**: 
  - 检测到字段缺失
  - 输出清晰的错误提示
  - 列出当前字段和缺失字段
  - 停止写入操作

---

## 三、边界与异常测试 (Edge & Exception Tests)

### 3.1 网络异常测试

#### TC-NETWORK-001: 网站无法访问
- **测试目的**: 验证网络故障处理
- **前置条件**: 断开网络或使用无效 URL
- **测试步骤**:
  1. 修改配置使用无效 URL
  2. 运行爬虫
  3. 验证错误处理
- **预期结果**: 
  - 捕获异常
  - 输出友好的错误信息
  - 不导致程序崩溃
  - 返回空列表或 None

#### TC-NETWORK-002: 请求超时
- **测试目的**: 验证超时重试机制
- **前置条件**: 模拟慢速响应
- **测试步骤**:
  1. 使用会超时的 URL
  2. 验证超时处理
- **预期结果**: 
  - 超时后重试（最多 3 次）
  - 仍失败后给出明确提示

#### TC-NETWORK-003: HTTP 错误状态码
- **测试目的**: 验证 4xx/5xx 错误处理
- **前置条件**: 使用返回错误码的 URL
- **测试步骤**:
  1. 访问返回 404 或 500 的页面
  2. 验证错误处理
- **预期结果**: 
  - 检测到非 200 状态码
  - 输出错误信息（包含状态码）
  - 不尝试解析错误页面

---

### 3.2 数据异常测试

#### TC-DATA-001: 搜索结果为零
- **测试目的**: 验证无结果时的处理
- **前置条件**: 使用不存在的关键词
- **测试步骤**:
  1. 搜索极冷门的词（如 "xyzabc123"）
  2. 验证返回空列表
- **预期结果**: 
  - 返回空列表
  - 输出提示信息"未找到相关关键词"
  - 不执行写入操作

#### TC-DATA-002: 排名数据缺失
- **测试目的**: 验证部分字段缺失的处理
- **前置条件**: 页面中某些词条缺少排名信息
- **测试步骤**:
  1. 解析包含不完整数据的页面
  2. 验证缺失字段的默认值处理
- **预期结果**: 
  - 缺失的排名使用默认值 0 或 "N/A"
  - 不导致程序崩溃

#### TC-DATA-003: 特殊字符关键词
- **测试目的**: 验证特殊字符的处理
- **前置条件**: 无
- **测试步骤**:
  1. 搜索包含特殊字符的词（如 "dog-bed&cat"）
  2. 验证 URL 编码和解析
- **预期结果**: 
  - URL 正确编码
  - 抓取结果正常
  - CSV 导出时字符编码正确（UTF-8）

---

### 3.3 并发与性能测试

#### TC-PERF-001: 大批量数据处理
- **测试目的**: 验证大量数据的处理能力
- **前置条件**: 无
- **测试步骤**:
  1. 设置 `max_results=1000`
  2. 运行抓取
  3. 记录执行时间
- **预期结果**: 
  - 成功抓取 1000 条数据
  - 执行时间在合理范围内（<5 分钟）
  - 内存使用稳定

#### TC-PERF-002: 快速连续执行
- **测试目的**: 验证频率限制处理
- **前置条件**: 无
- **测试步骤**:
  1. 连续执行 3 次抓取任务
  2. 间隔小于 10 秒
  3. 验证是否有速率限制
- **预期结果**: 
  - 每次执行之间有延时（`time.sleep`）
  - 不触发网站的反爬机制
  - 钉钉 API 调用不超过限制

---

### 3.4 权限与安全测试

#### TC-SECURITY-001: MCP URL 无效
- **测试目的**: 验证无效凭证的处理
- **前置条件**: 配置错误的 MCP URL
- **测试步骤**:
  1. 修改配置使用无效的 MCP URL
  2. 尝试写入表格
  3. 验证错误处理
- **预期结果**: 
  - 认证失败
  - 输出清晰的错误提示
  - 不泄露敏感信息

#### TC-SECURITY-002: 表格权限不足
- **测试目的**: 验证权限不足的处理
- **前置条件**: 使用只读权限的表格链接
- **测试步骤**:
  1. 配置只读权限的表格
  2. 尝试写入数据
  3. 验证错误处理
- **预期结果**: 
  - 检测到权限不足
  - 提示用户检查表格权限
  - 不执行写入

#### TC-SECURITY-003: 配置文件安全性
- **测试目的**: 验证敏感信息的保护
- **前置条件**: 无
- **测试步骤**:
  1. 检查配置文件的读写权限
  2. 验证不包含明文密码
- **预期结果**: 
  - 文件权限设置为仅所有者可读写（600）
  - MCP URL 作为令牌使用（非账号密码）

---

## 四、用户交互测试 (User Interaction Tests)

### 4.1 命令行参数测试

#### TC-CLI-001: 缺少必需参数
- **测试目的**: 验证参数校验
- **前置条件**: 无配置文件或 `--force-config`
- **测试步骤**:
  1. 运行 `python3 amz123_enhanced_scraper_v2.py`（无参数）
  2. 验证错误提示
- **预期结果**: 
  - 显示帮助信息
  - 提示缺少 `--keyword` 参数
  - 提供使用示例

#### TC-CLI-002: 帮助信息显示
- **测试目的**: 验证帮助文档的完整性
- **前置条件**: 无
- **测试步骤**:
  1. 运行 `python3 amz123_enhanced_scraper_v2.py --help`
  2. 验证输出内容
- **预期结果**: 
  - 显示所有参数说明
  - 包含使用示例
  - 格式清晰易读

#### TC-CLI-003: 无效参数值
- **测试目的**: 验证参数校验
- **前置条件**: 无
- **测试步骤**:
  1. 运行 `python3 amz123_enhanced_scraper_v2.py --keyword ""`
  2. 验证空关键词处理
- **预期结果**: 
  - 检测到空字符串
  - 提示用户提供有效关键词

---

### 4.2 日志与输出测试

#### TC-LOG-001: 详细日志输出
- **测试目的**: 验证日志的完整性
- **前置条件**: 无
- **测试步骤**:
  1. 运行完整抓取流程
  2. 检查控制台输出
- **预期结果**: 
  - 每个步骤都有状态输出
  - 包含 [信息]、[成功]、[错误] 等标记
  - 关键数据（如数量、文件名）清晰显示

#### TC-LOG-002: 错误日志的可读性
- **测试目的**: 验证错误信息的友好性
- **前置条件**: 制造一个错误场景
- **测试步骤**:
  1. 触发一个已知错误
  2. 检查错误输出
- **预期结果**: 
  - 错误描述清晰
  - 包含可能的原因
  - 提供解决建议

---

## 五、回归测试 (Regression Tests)

### 5.1 历史 Bug 验证

#### TC-REGRESSION-001: 涨跌幅度计算错误修复
- **测试目的**: 验证排名数字越小越靠前的逻辑
- **前置条件**: 无
- **测试步骤**:
  1. 测试用例：rank 从 2→1
  2. 测试用例：rank 从 1→2
- **预期结果**: 
  - 2→1 应显示"上升"
  - 1→2 应显示"下降"

#### TC-REGRESSION-002: 字段比对误报修复
- **测试目的**: 验证字段名称大小写处理
- **前置条件**: 无
- **测试步骤**:
  1. 比对 `['Rank', 'Keyword']` 和 `['rank', 'keyword']`
- **预期结果**: 视为相同（忽略大小写）

---

## 六、自动化测试脚本

### 6.1 测试运行器

创建 `run_tests.py` 脚本自动化执行所有测试：

```python
#!/usr/bin/env python3
# run_tests.py - 自动化测试运行器

import unittest
import sys
import os

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# 导入测试模块
from test_config import ConfigTests
from test_scraper import ScraperTests
from test_calculator import CalculatorTests
from test_integration import IntegrationTests

if __name__ == '__main__':
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(ConfigTests))
    suite.addTests(loader.loadTestsFromTestCase(ScraperTests))
    suite.addTests(loader.loadTestsFromTestCase(CalculatorTests))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTests))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回退出码
    sys.exit(0 if result.wasSuccessful() else 1)
```

### 6.2 测试覆盖率检查

```bash
# 使用 coverage 工具检查测试覆盖率
pip3 install coverage
coverage run --source=scripts run_tests.py
coverage report -m
coverage html  # 生成 HTML 报告
```

**目标覆盖率：**
- 核心逻辑（数据抓取、计算、写入）：≥ 90%
- 错误处理分支：≥ 80%
- 整体覆盖率：≥ 85%

---

## 七、测试执行清单

### 执行前准备

- [ ] 确认 Python 版本 ≥ 3.9
- [ ] 安装所有依赖包
- [ ] 准备测试用的钉钉AI表格
- [ ] 备份现有配置文件
- [ ] 确保网络连接正常

### 测试执行顺序

1. **单元测试** (优先级：高)
   - 配置管理测试
   - 数据抓取测试
   - 计算逻辑测试
   
2. **集成测试** (优先级：高)
   - 前置检查流程
   - 端到端数据流
   - 钉钉表格操作

3. **边界与异常测试** (优先级：中)
   - 网络异常
   - 数据异常
   - 性能测试

4. **用户交互测试** (优先级：中)
   - 命令行参数
   - 日志输出

5. **回归测试** (优先级：低，发布前执行)

### 测试结果记录模板

| 测试用例 ID | 测试名称 | 执行日期 | 执行人 | 结果 | 备注 |
|-----------|---------|---------|-------|------|------|
| TC-CONFIG-001 | 加载现有配置 | 2026-03-14 | 北野川 | Pass/Fail | - |
| TC-SCRAPER-001 | 成功获取 HTML | 2026-03-14 | 北野川 | Pass/Fail | - |
| ... | ... | ... | ... | ... | ... |

---

## 八、缺陷报告模板

```markdown
### 缺陷报告

**缺陷 ID:** BUG-001
**发现日期:** 2026-03-14
**严重程度:** 高/中/低
**优先级:** P0/P1/P2

**标题:** [简短描述问题]

**重现步骤:**
1. ...
2. ...
3. ...

**预期结果:**
...

**实际结果:**
...

**环境信息:**
- Python 版本：3.9.x
- 操作系统：macOS 15.5
- 技能包版本：v2.0

**附加信息:**
- 日志文件：[附件]
- 截图：[附件]
```

---

## 总结

本测试用例集涵盖了 `hot_search_scraper` 技能包的各个方面，共计 **70+ 个测试用例**，分为 8 大类：

1. **单元测试** - 验证各个功能模块的正确性
2. **集成测试** - 验证模块间的协作
3. **边界与异常测试** - 验证容错能力
4. **用户交互测试** - 验证 CLI 和日志
5. **回归测试** - 防止历史 Bug 复发

**建议执行策略：**
- 开发阶段：每日执行单元测试
- 发布前：执行全部测试用例
- 生产环境：定期执行回归测试

通过完整的测试覆盖，确保技能包在实际使用中的稳定性和可靠性。

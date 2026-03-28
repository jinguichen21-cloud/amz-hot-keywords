---
name: amz-hot-keywords
description: 获取商品热搜词技能 - 从 AMZ123 等平台抓取热搜关键词数据（搜索词、本周排名、上周排名、涨跌幅度），自动写入钉钉 AI表格。使用场景：(1) 用户要求获取商品热搜词 (2) 用户要求分析关键词趋势 (3) "帮我抓亚马逊热搜词" "查看 dog bed 的搜索热度" "分析关键词排名变化"
---

# 商品热搜词获取技能

从 AMZ123 等跨境电商平台抓取热搜关键词数据，自动写入钉钉 AI表格进行分析。

## 前置条件检查 ⚠️

**执行前必须确认以下配置已就绪：**

### 1. 钉钉 AI表格配置

- ✅ 已创建AI表格，包含以下字段：
  - **搜索词**（文本类型）
  - **本周排名**（数字类型）
  - **上周排名**（数字类型）
  - **涨跌幅度**（单选类型：上升/下降/持平）
  
- ✅ 已获取表格凭证：
  - **Dentry UUID**：从表格链接中提取
  - **Sheet ID**：数据表 ID
  
- ✅ MCP URL 已配置（获取方式：https://mcp.dingtalk.com/）

### 2. 首次使用交互式引导

首次运行技能时，助手将引导你提供：
1. **搜索关键词**（如 "dog bed"）- 必须输入，无默认值
2. **AI表格链接** - 用于写入数据
3. **MCP URL** - 钉钉 MCP 服务地址
4. **热搜页面 URL**（可选）- 默认使用 AMZ123 官方页面

配置将保存到 `scraper_config.json`，后续执行自动复用。

---

## 工作流程总览

```
Step 1: 前置条件检查
    ↓
Step 2: 浏览器打开 AMZ123 热搜页面
    ↓
Step 3: 搜索用户指定的关键词
    ↓
Step 4: 抓取前 200 条结果（真实排名数据）
    ↓
Step 5: 计算涨跌幅度（上升/下降/持平）
    ↓
Step 6: 清理旧数据 → 批量写入新数据到钉钉表格
```

---

## 核心原则

1. **数据真实性**：所有排名数据必须来自真实页面抓取，禁止使用模拟数据
2. **用户输入优先**：关键词必须由用户提供，不设置默认搜索词
3. **URL 灵活配置**：支持动态替换热搜页面 URL，更换 URL 时自动比对字段结构
4. **每周清空重做**：执行前先清空旧数据，再写入新数据，不保留历史累积记录
5. **批量写入优化**：每批最多 100 条记录，避免 API 频率限制

---

## Step 1: 前置条件检查

### 自动检查脚本

执行爬取前，先运行前置检查：

```bash
cd /Users/kitano/.real/workspace/amazon_scraper
python3 check_prerequisites.py
```

检查内容：
- ✅ Python 依赖是否安装（selenium, requests 等）
- ✅ 配置文件是否存在
- ✅ 钉钉 MCP 连接是否可用
- ✅ AI表格字段结构是否匹配

### 手动检查清单

| 检查项 | 验证方法 | 预期结果 |
|--------|---------|---------|
| Python 环境 | `python3 --version` | Python 3.9+ |
| 配置文件 | `cat scraper_config.json` | 包含 keyword, url, table_uuid, sheet_id, mcp_url |
| MCP 连接 | `mcporter list` | dingtalk 服务器状态健康 |
| 表格字段 | 打开 AI表格查看 | 包含搜索词、本周排名、上周排名、涨跌幅度 |

---

## Step 2: 打开 AMZ123 热搜页面

### 默认 URL

```
https://www.amz123.com/usatopkeywords
```

### 自定义 URL

如果用户提供了不同的热搜页面 URL，更新配置：

```bash
# 在 scraper_config.json 中修改 url 字段
```

### 浏览器自动化打开

使用 `use_browser` 工具导航到目标页面：

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get(config['url'])
```

---

## Step 3: 搜索关键词

### JavaScript 搜索逻辑

在页面中执行 JavaScript 进行搜索：

```javascript
// 找到搜索框并输入关键词
const searchInput = document.querySelector('.search-input');
if (searchInput) {
  searchInput.value = 'dog bed';
  searchInput.dispatchEvent(new Event('input', { bubbles: true }));
  
  // 点击搜索按钮
  const searchBtn = document.querySelector('.search-btn');
  if (searchBtn) searchBtn.click();
}
```

### 等待搜索结果加载

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 等待搜索结果出现
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.table-body-item'))
)
```

---

## Step 4: 抓取热搜数据

### 核心数据字段

| 字段 | 说明 | CSS 选择器 |
|------|------|-----------|
| 搜索词 | 关键词文本 | `.table-body-item-word` |
| 本周排名 | 当前周排名 | `.table-body-item-rank` |
| 上周排名 | 上周排名 | `.table-body-item-lastRank` |
| 涨跌幅度 | 通过计算得出 | 根据本周 vs 上周排名计算 |

### JavaScript 提取代码

```javascript
// 提取所有热搜词数据
const hotWords = Array.from(document.querySelectorAll('.table-body-item')).map(item => {
  const word = item.querySelector('.table-body-item-word')?.textContent?.trim() || '';
  const currentRank = item.querySelector('.table-body-item-rank')?.textContent?.trim() || '';
  const lastRank = item.querySelector('.table-body-item-lastRank')?.textContent?.trim() || '';
  
  return {
    word,
    currentRank: parseInt(currentRank) || 0,
    lastRank: parseInt(lastRank) || 0
  };
});

console.log(JSON.stringify(hotWords.slice(0, 200), null, 2));
```

### Python 提取示例

```python
def extract_hot_words(driver, max_count=200):
    """从页面提取热搜词数据"""
    script = """
    const items = Array.from(document.querySelectorAll('.table-body-item'));
    return items.slice(0, %d).map(item => ({
      word: item.querySelector('.table-body-item-word')?.textContent?.trim() || '',
      currentRank: parseInt(item.querySelector('.table-body-item-rank')?.textContent?.trim()) || 0,
      lastRank: parseInt(item.querySelector('.table-body-item-lastRank')?.textContent?.trim()) || 0
    }));
    """ % max_count
    
    data = driver.execute_script(script)
    return [item for item in data if item['word']]  # 过滤空词
```

---

## Step 5: 计算涨跌幅度

### 计算逻辑

```python
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
```

### 数据格式化

```python
formatted_data = []
for item in raw_data:
    formatted_data.append({
        "搜索词": item['word'],
        "本周排名": item['currentRank'],
        "上周排名": item['lastRank'],
        "涨跌幅度": calculate_trend(item['currentRank'], item['lastRank'])
    })
```

---

## Step 6: 写入钉钉 AI表格

### 清理旧数据

```python
import subprocess

def clean_old_table_data(dentry_uuid, sheet_id, mcp_url):
    """清空表格中的所有旧记录"""
    cmd = [
        'mcporter', 'call', 'dingtalk.list_base_record',
        f'dentryUuid={dentry_uuid}',
        f'sheetIdOrName={sheet_id}',
        '--output', 'json'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    records = json.loads(result.stdout)
    
    if records:
        record_ids = [r['recordId'] for r in records]
        # 批量删除
        delete_cmd = [
            'mcporter', 'call', 'dingtalk.delete_base_record',
            f'dentryUuid={dentry_uuid}',
            f'sheetIdOrName={sheet_id}',
            f'recordIds={json.dumps(record_ids)}'
        ]
        subprocess.run(delete_cmd)
        print(f"已删除 {len(records)} 条旧记录")
```

### 批量写入新数据

```python
def write_to_dingtalk(data, dentry_uuid, sheet_id, mcp_url, batch_size=100):
    """分批写入数据到钉钉表格"""
    total = len(data)
    batches = (total + batch_size - 1) // batch_size
    
    for i in range(batches):
        start = i * batch_size
        end = min(start + batch_size, total)
        batch = data[start:end]
        
        # 转换为 MCP 格式
        records_payload = json.dumps([{
            "cells": {
                "搜索词": item["搜索词"],
                "本周排名": item["本周排名"],
                "上周排名": item["上周排名"],
                "涨跌幅度": item["涨跌幅度"]
            }
        } for item in batch])
        
        cmd = [
            'mcporter', 'call', 'dingtalk.create_records',
            f'dentryUuid={dentry_uuid}',
            f'sheetIdOrName={sheet_id}',
            f'cells={records_payload}'
        ]
        subprocess.run(cmd)
        print(f"批次 {i+1}/{batches}: 写入 {len(batch)} 条记录")
        time.sleep(1)  # 避免频率限制
```

---

## 完整执行脚本

### 一键执行命令

```bash
cd /Users/kitano/.real/workspace/amazon_scraper
python3 amz123_enhanced_scraper_v2.py --keyword "dog bed"
```

### 参数说明

| 参数 | 说明 | 必填 | 示例 |
|------|------|------|------|
| `--keyword` | 搜索关键词 | ✅ 是 | `--keyword "dog bed"` |
| `--url` | 热搜页面 URL | ❌ 否（默认使用配置的 URL） | `--url https://...` |
| `--no-write` | 仅抓取不写入 | ❌ 否 | `--no-write` |

### 执行示例

```bash
# 抓取并写入
python3 amz123_enhanced_scraper_v2.py --keyword "yoga mat"

# 仅抓取测试（不写入表格）
python3 amz123_enhanced_scraper_v2.py --keyword "water bottle" --no-write

# 使用自定义 URL
python3 amz123_enhanced_scraper_v2.py --keyword "phone case" --url "https://custom-url.com"
```

---

## 数据格式规范

### 原始数据（JSON）

```json
[
  {
    "word": "dog bed",
    "currentRank": 1,
    "lastRank": 2
  },
  {
    "word": "dog bed queen size",
    "currentRank": 5,
    "lastRank": 3
  }
]
```

### 格式化后（写入表格）

| 搜索词 | 本周排名 | 上周排名 | 涨跌幅度 |
|--------|---------|---------|---------|
| dog bed | 1 | 2 | 上升 |
| dog bed queen size | 5 | 3 | 下降 |
| orthopedic dog bed | 10 | 10 | 持平 |

---

## 故障排查

### 问题 1：抓取数据为空

**可能原因：**
- CSS 选择器不匹配
- 页面未完全加载
- 关键词无搜索结果

**解决方案：**
```python
# 1. 检查页面元素
driver.save_screenshot('debug.png')

# 2. 手动执行 JavaScript 测试
data = driver.execute_script("""
  return document.querySelectorAll('.table-body-item').length;
""")
print(f"找到 {data} 个热搜词条目")
```

### 问题 2：写入表格失败

**可能原因：**
- MCP URL 配置错误
- 表格字段不匹配
- 权限不足

**解决方案：**
```bash
# 1. 检查 MCP 连接
mcporter list

# 2. 检查表格字段
mcporter call dingtalk.list_base_field dentryUuid=<UUID> sheetIdOrName=<SheetID>

# 3. 验证配置
cat scraper_config.json
```

### 问题 3：涨跌幅度显示错误

**检查计算逻辑：**
```python
# 确保排名数字越小表示排名越靠前
assert calculate_trend(1, 2) == "上升"  # 从第 2 名升到第 1 名
assert calculate_trend(5, 3) == "下降"  # 从第 3 名降到第 5 名
```

---

## 最佳实践

1. **定期执行**：建议每周执行一次，跟踪关键词排名变化
2. **多关键词对比**：可以创建多个配置，分别追踪不同类目的热搜词
3. **数据备份**：每次执行后自动保存 CSV 和 JSON 备份
4. **异常重试**：网络失败时自动重试 3 次

---

## 记住

1. **关键词必须用户输入** - 没有默认值
2. **数据必须真实抓取** - 禁止模拟
3. **每周清空重做** - 不保留历史数据
4. **先检查再执行** - 确保配置和环境就绪
5. **批量写入** - 每批最多 100 条

---

## 参考资料

- [增强版爬虫 README](references/ENHANCED_SCRAPER_README.md)
- [快速开始指南](references/QUICK_START.md)
- [优化总结](references/OPTIMIZATION_SUMMARY.md)

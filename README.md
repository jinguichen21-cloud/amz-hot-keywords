# 商品热搜词获取技能包

从 AMZ123 等跨境电商平台抓取热搜关键词数据，自动写入钉钉 AI表格进行分析。

---

## 📦 技能包结构

```
amazon_scraper_skill/
├── SKILL.md                          # 核心技能文档（必读）
├── manifest.json                     # 技能包清单
├── README.md                         # 本文件
├── scripts/
│   ├── amz123_enhanced_scraper_v2.py    # 主爬虫脚本
│   ├── scraper_config.json              # 配置文件（首次运行后生成）
│   └── check_prerequisites.py           # 前置条件检查脚本
└── references/
    ├── QUICK_START.md                   # 快速开始指南
    ├── OPTIMIZATION_SUMMARY.md          # 优化总结
    └── ENHANCED_SCRAPER_README.md       # 增强版使用说明
```

---

## ⚡ 快速开始

### 5 分钟上手指南

#### Step 1: 准备工作

1. **创建钉钉 AI表格**，包含以下字段：
   - 搜索词（文本）
   - 本周排名（数字）
   - 上周排名（数字）
   - 涨跌幅度（单选：上升/下降/持平）

2. **获取表格凭证**：
   - Dentry UUID（从表格链接提取）
   - Sheet ID（数据表 ID）

3. **获取 MCP URL**：
   - 访问：https://mcp.dingtalk.com/

#### Step 2: 运行前置检查

```bash
cd /Users/kitano/.real/workspace/amazon_scraper_skill/scripts
python3 check_prerequisites.py
```

#### Step 3: 执行爬取任务

```bash
# 抓取指定关键词的热搜数据并写入表格
python3 amz123_enhanced_scraper_v2.py --keyword "dog bed"
```

---

## 🎯 核心功能

✅ **自定义关键词搜索** - 支持用户输入任意关键词，搜索相关热词（前 200 条）  
✅ **动态 URL 配置** - 支持更换热搜页面 URL，自动比对字段结构  
✅ **数据完整性保障** - 确保排名、涨跌幅度等字段准确无误  
✅ **配置持久化** - 首次配置后自动保存，后续执行复用  
✅ **批量写入优化** - 每批最多 100 条记录，避免 API 频率限制  

---

## 📊 输出数据格式

### 示例数据

| 搜索词 | 本周排名 | 上周排名 | 涨跌幅度 |
|--------|---------|---------|---------|
| dog bed | 1 | 2 | 上升 |
| dog bed queen size | 5 | 3 | 下降 |
| orthopedic dog bed | 10 | 10 | 持平 |

### 本地文件

- `{keyword}_keywords_{YYYYMMDD}.csv` - CSV 格式原始数据
- `{keyword}_data_{YYYYMMDD}.json` - JSON 格式格式化数据

### 钉钉 AI表格

数据自动写入配置的 AI表格，可直接在钉钉中查看和分析。

---

## 🔧 常用命令

### 基本用法

```bash
# 抓取并写入
python3 scripts/amz123_enhanced_scraper_v2.py --keyword "yoga mat"

# 仅抓取测试（不写入）
python3 scripts/amz123_enhanced_scraper_v2.py --keyword "water bottle" --no-write

# 使用自定义 URL
python3 scripts/amz123_enhanced_scraper_v2.py --keyword "phone case" \
  --url "https://custom-amz123.com/hotword.htm"
```

### 前置检查

```bash
# 验证环境和配置
python3 scripts/check_prerequisites.py
```

### 强制重新配置

```bash
# 清除旧配置，重新输入
python3 scripts/amz123_enhanced_scraper_v2.py --force-config
```

---

## 📖 详细文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](./SKILL.md) | **核心技能文档** - 完整工作流程、故障排查、最佳实践 |
| [QUICK_START.md](./references/QUICK_START.md) | 5 分钟快速上手指南 |
| [OPTIMIZATION_SUMMARY.md](./references/OPTIMIZATION_SUMMARY.md) | 技术实现细节和优化总结 |
| [ENHANCED_SCRAPER_README.md](./references/ENHANCED_SCRAPER_README.md) | 增强版爬虫使用说明 |

---

## ⚠️ 重要原则

1. **关键词必须用户输入** - 没有默认值
2. **数据必须真实抓取** - 来自 AMZ123 真实页面，禁止模拟
3. **每周清空重做** - 不保留历史累积记录
4. **先检查再执行** - 运行 `check_prerequisites.py` 确保环境就绪
5. **批量写入优化** - 每批最多 100 条记录

---

## 🛠️ 依赖要求

### Python 环境

- Python >= 3.9

### Python 包

```bash
pip3 install selenium requests beautifulsoup4 pandas fake-useragent
```

### 工具

- `mcporter` CLI（钉钉 MCP 客户端）
- Chrome 浏览器（用于浏览器自动化）

---

## 🐛 常见问题

### Q: 抓取数据为空？

**A:** 检查网络连接和页面结构，使用 `--no-write` 参数测试。

### Q: 写入表格失败？

**A:** 验证钉钉表格字段是否匹配，检查 MCP 连接状态。

### Q: MCP 连接超时？

**A:** 运行 `mcporter list` 检查服务器状态，重新获取 MCP URL。

---

## 📝 配置示例

### scraper_config.json

```json
{
  "keyword": "dog bed",
  "url": "https://www.amz123.com/hotword.htm",
  "table_uuid": "bxxxxxxxxxxxxx",
  "sheet_id": "vxxxxxxxxxx",
  "mcp_url": "https://mcp.dingtalk.com/xxx/xxx"
}
```

---

## 📞 技术支持

- 技能文档：[SKILL.md](./SKILL.md)
- 快速开始：[QUICK_START.md](./references/QUICK_START.md)
- 优化总结：[OPTIMIZATION_SUMMARY.md](./references/OPTIMIZATION_SUMMARY.md)

---

## 📅 版本信息

- **当前版本**: 1.0.0
- **创建日期**: 2026-03-14
- **作者**: 北野川
- **组织**: bug 砖家

---

## 🎓 学习路径

1. ✅ 阅读 [QUICK_START.md](./references/QUICK_START.md) - 5 分钟快速上手
2. ✅ 运行 `check_prerequisites.py` - 验证环境就绪
3. ✅ 执行第一次爬取 - 体验完整流程
4. ✅ 阅读 [SKILL.md](./SKILL.md) - 深入理解工作原理
5. ✅ 阅读 [OPTIMIZATION_SUMMARY.md](./references/OPTIMIZATION_SUMMARY.md) - 技术细节和优化技巧

---

**开始使用 →** `python3 scripts/amz123_enhanced_scraper_v2.py --keyword "<你的关键词>"`

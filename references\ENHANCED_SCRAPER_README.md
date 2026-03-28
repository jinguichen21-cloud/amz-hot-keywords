#增强版爬虫使用说明

##功能特性

✅ **自定义关键词搜索** - 支持用户输入任意关键词，搜索相关热词（前 200 条）  
✅ **动态 URL 配置** - 支持更换热搜页面 URL，自动比对字段结构  
✅ **数据完整性保障** - 确保排名、涨跌幅度等字段准确无误  
✅ **配置持久化** -首次配置后自动保存，后续执行复用  

---

## 快速开始

### 1.基本用法

```bash
cd /Users/kitano/.real/workspace/amazon_scraper_skill/scripts

# 抓取指定关键词的热搜数据并写入表格
python3 amz123_enhanced_scraper_v2.py --keyword "dog bed"
```

### 2.参数说明

| 参数 | 说明 | 必填 | 示例 |
|------|------|------|------|
| `--keyword` | 搜索关键词 | ✅ 是 | `--keyword "dog bed"` |
| `--url` | 热搜页面 URL | ❌ 否（使用配置的 URL） | `--url https://...` |
| `--no-write` | 仅抓取不写入 | ❌ 否 | `--no-write` |
| `--force-config` |强制重新配置| ❌ 否 | `--force-config` |

### 3. 使用示例

```bash
#示例1:基本用法（抓取并写入）
python3 amz123_enhanced_scraper_v2.py --keyword "yoga mat"

#示例2:测试模式（仅抓取，验证数据）
python3 amz123_enhanced_scraper_v2.py --keyword "water bottle" --no-write

#示例3:使用自定义 URL
python3 amz123_enhanced_scraper_v2.py --keyword "phone case" \
  --url "https://custom-amz123.com/hotword.htm"

#示例4:强制重新配置
python3 amz123_enhanced_scraper_v2.py --force-config
```

---

## 工作流程

```
Step 1:加载配置文件
    ↓
Step 2: 浏览器打开 AMZ123 页面
    ↓
Step 3: 搜索指定关键词
    ↓
Step 4:提取前 200 条结果
    ↓
Step 5: 计算涨跌幅度
    ↓
Step 6:保存到本地CSV/JSON
    ↓
Step 7: (可选)写入钉钉 AI表格
```

---

##输出文件

执行完成后生成以下文件：

### 1. CSV 格式原始数据

文件名：`{keyword}_keywords_{YYYYMMDD}.csv`

内容示例：
```csv
rank,keyword,last_rank,trend
1,dog bed,2,上升
5,dog bed queen size,3,下降
```

### 2. JSON 格式格式化数据

文件名：`{keyword}_data_{YYYYMMDD}.json`

内容示例：
```json
[
  {
    "搜索词": "dog bed",
    "本周排名": 1,
    "上周排名": 2,
    "涨跌幅度": "上升"
  }
]
```

### 3.配置文件

`scraper_config.json` - 保存用户配置：
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

## 数据准确性保障

### 1.真实数据抓取

- ✅ 从 AMZ123 页面直接提取真实排名数据
- ✅ 禁止使用模拟数据或估算值
- ✅ 每次执行都重新抓取最新数据

### 2. 涨跌幅度计算

```python
def calculate_trend(current_rank, last_rank):
    if last_rank == 0 or last_rank is None:
        return "上升"  # 新上榜
    elif current_rank < last_rank:
        return "上升"  #数字越小排名越靠前
    elif current_rank > last_rank:
        return "下降"
    else:
        return "持平"
```

### 3.字段校验

执行前自动检查钉钉表格字段是否匹配：
-搜索词（文本）
- 本周排名（数字）
- 上周排名（数字）
-涨跌幅度（单选：上升/下降/持平）

---

## 故障排查

### 问题 1：抓取数据为空

**症状：**
```
[警告] 未能从页面提取到关键词信息
```

**解决方案：**
```bash
# 1. 检查网络连接
curl https://www.amz123.com/hotword.htm

# 2. 手动打开浏览器验证
open https://www.amz123.com/hotword.htm

# 3. 使用 --no-write 测试
python3 amz123_enhanced_scraper_v2.py --keyword "test" --no-write
```

### 问题 2：写入钉钉表格失败

**症状：**
```
[错误] 添加记录失败：字段不存在
```

**解决方案：**
1. 打开钉钉 AI表格
2. 确认包含以下 4 个字段：
   - 搜索词
   - 本周排名
   - 上周排名
   - 涨跌幅度
3. 重新运行前置检查

### 问题 3：MCP 连接超时

**症状：**
```
[错误] 获取表格字段失败：Connection timeout
```

**解决方案：**
```bash
# 1. 检查 MCP 服务器状态
mcporter list

# 2.验证MCP URL 配置
cat scraper_config.json | grep mcp_url

# 3. 重新获取 MCP URL
访问：https://mcp.dingtalk.com/
```

---

## 最佳实践

### 1. 定期执行

建议每周执行一次，跟踪关键词排名变化：

```bash
# 添加到crontab（每周一上午 9点）
0 9 * * 1 cd /Users/kitano/.real/workspace/amazon_scraper_skill/scripts && \
  python3 amz123_enhanced_scraper_v2.py --keyword "dog bed"
```

### 2.多关键词对比

为不同产品线创建独立配置：

```bash
# 宠物用品
python3 amz123_enhanced_scraper_v2.py --keyword "pet supplies"

# 运动器材
python3 amz123_enhanced_scraper_v2.py --keyword "sports equipment"

#家居生活
python3 amz123_enhanced_scraper_v2.py --keyword "home storage"
```

### 3. 数据备份

每次执行自动生成 CSV 和 JSON 备份，建议：
- 本地保留最近 4 周数据
- 钉钉表格作为主分析平台
-定期导出Excel 进行深度分析

---

## 性能优化

### 1. 批量写入

-单次最多写入100 条记录
-超过 100条自动分批处理
-批次间隔1-2秒，避免频率限制

### 2.请求优化

- 使用随机User-Agent避免反爬
-请求间隔1-3秒随机延迟
-失败自动重试（最多3 次）

### 3.资源管理

- 浏览器自动启动/关闭
-临时文件自动清理
-内存占用优化（适合长时间运行）

---

## 常见问题FAQ

### Q:为什么搜索结果不足 200条？

**A:** 某些关键词的搜索结果本身就少于200 条，这是正常现象。脚本会接受实际数量（如 102 条），但会在日志中提示。

### Q:可以更换其他平台吗？

**A:**当前版本仅支持AMZ123平台。如需支持其他平台，需要修改爬虫逻辑。

### Q:如何查看历史数据？

**A:** 
1.本地CSV/JSON文件按日期命名，可直接查看
2.钉钉表格默认每周清空，如需保留历史，修改`clear_first=False`

### Q:能否同时追踪多个关键词？

**A:**可以。为每个关键词创建独立的配置文件，分别执行即可。

---

## 技术支持

- 查看完整技能文档：[SKILL.md](../SKILL.md)
- 查看快速开始：[QUICK_START.md](./QUICK_START.md)
- 查看优化总结：[OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)

---

## 记住

✅ **关键词必须用户输入** - 没有默认值  
✅ **数据真实抓取** - 来自 AMZ123 真实页面  
✅ **每周清空重做** - 不保留历史数据  
✅ **先检查再执行** - 运行 `check_prerequisites.py`  
✅ **批量写入优化** - 每批最多 100 条记录

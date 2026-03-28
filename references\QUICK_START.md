# 商品热搜词技能 - 快速开始指南

## 5 分钟快速上手

### Step 1: 准备工作 (2 分钟)

#### 1.1 创建钉钉 AI表格

1. 打开钉钉，进入 **AI表格**
2. 点击 **新建表格**
3. 添加以下字段（字段名必须完全一致）：

| 字段名 | 字段类型 | 说明 |
|--------|---------|------|
| 搜索词 | 文本 | 关键词文本 |
| 本周排名 | 数字 | 当前周排名 |
| 上周排名 | 数字 | 上周排名 |
| 涨跌幅度 | 单选 | 选项：上升、下降、持平 |

#### 1.2 获取表格凭证

1. 打开刚创建的表格
2. 从 URL 中提取 **Dentry UUID**：
   ```
   https://dingtalk.com/base/.../<DENTRY_UUID>/...
                                      ^^^^^^^^^^^^
   ```
3. 点击表格右上角 **...** → **数据表信息** → 复制 **Sheet ID**

#### 1.3 获取 MCP URL

访问：https://mcp.dingtalk.com/

按照页面指引获取你的专属 MCP URL。

---

### Step 2: 首次运行配置 (3 分钟)

#### 2.1 运行前置检查

```bash
cd /Users/kitano/.real/workspace/amazon_scraper_skill/scripts
python3 check_prerequisites.py
```

如果所有检查通过，继续下一步。

#### 2.2 交互式配置

首次运行脚本会自动引导你配置：

```bash
python3 amz123_enhanced_scraper_v2.py --keyword "dog bed"
```

脚本会提示你输入：
- ✅ 搜索关键词（如 "dog bed"）
- ✅ AI表格链接（完整 URL）
- ✅ MCP URL（从 https://mcp.dingtalk.com/ 获取）
- ✅ 热搜页面 URL（可选，默认使用 AMZ123 官方页面）

配置将保存到 `scraper_config.json`，后续执行自动复用。

---

### Step 3: 执行爬取任务

#### 3.1 基本用法

```bash
# 抓取指定关键词的热搜数据并写入表格
python3 amz123_enhanced_scraper_v2.py --keyword "yoga mat"
```

#### 3.2 测试模式（仅抓取不写入）

```bash
# 验证数据抓取是否正常
python3 amz123_enhanced_scraper_v2.py --keyword "water bottle" --no-write
```

#### 3.3 使用自定义 URL

```bash
# 使用不同的热搜页面
python3 amz123_enhanced_scraper_v2.py --keyword "phone case" \
  --url "https://custom-amz123-mirror.com/hotword.htm"
```

---

### Step 4: 查看结果

#### 4.1 本地文件

执行完成后，在当前目录生成：
- `dogbed_keywords_YYYYMMDD.csv` - CSV 格式原始数据
- `dogbed_data_YYYYMMDD.json` - JSON 格式格式化数据

#### 4.2 钉钉 AI表格

打开钉钉，进入你配置的 AI表格，应该能看到：

| 搜索词 | 本周排名 | 上周排名 | 涨跌幅度 |
|--------|---------|---------|---------|
| dog bed | 1 | 2 | 上升 |
| dog bed queen size | 5 | 3 | 下降 |
| orthopedic dog bed | 10 | 10 | 持平 |

---

## 常见问题

### Q1: "配置文件不存在"

**解决：** 首次运行时会自动创建，按提示输入配置即可。

### Q2: "MCP 连接失败"

**解决：**
1. 检查 `mcporter list` 是否显示 dingtalk 服务器
2. 确认 MCP URL 配置正确
3. 访问 https://mcp.dingtalk.com/ 重新获取

### Q3: "抓取数据为空"

**可能原因：**
- 网络连接问题
- 关键词无搜索结果
- 页面结构变化

**解决：**
```bash
# 使用 --no-write 测试
python3 amz123_enhanced_scraper_v2.py --keyword "test" --no-write

# 检查生成的 CSV 文件
cat test_keywords_*.csv
```

### Q4: "表格字段不匹配"

**解决：**
1. 打开 AI表格
2. 确保包含以下 4 个字段（字段名必须完全一致）：
   - 搜索词
   - 本周排名
   - 上周排名
   - 涨跌幅度
3. 重新运行前置检查

---

## 进阶用法

### 多关键词批量追踪

创建多个配置文件，分别追踪不同类目的热搜词：

```bash
# 宠物用品类目
cp scraper_config.json config_pet.json
# 修改 config_pet.json 中的 keyword 为 "pet supplies"

# 运动器材类目
cp scraper_config.json config_sports.json
# 修改 config_sports.json 中的 keyword 为 "sports equipment"
```

### 定时执行

使用系统 cron 定时任务，每周自动执行：

```bash
# 编辑 crontab
crontab -e

# 添加每周一上午 9 点执行
0 9 * * 1 cd /Users/kitano/.real/workspace/amazon_scraper_skill/scripts && \
  python3 amz123_enhanced_scraper_v2.py --keyword "dog bed"
```

### 数据导出分析

从钉钉表格导出数据到 Excel 进行分析：

1. 打开钉钉 AI表格
2. 点击右上角 **...** → **导出为 Excel**
3. 使用 Excel 或 Google Sheets 进行数据分析

---

## 获取帮助

- 查看完整文档：[SKILL.md](../SKILL.md)
- 查看优化总结：[OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)
- 查看增强版说明：[ENHANCED_SCRAPER_README.md](./ENHANCED_SCRAPER_README.md)

---

## 记住

✅ **关键词必须用户提供** - 没有默认值  
✅ **数据真实抓取** - 来自 AMZ123 真实页面  
✅ **每周清空重做** - 不保留历史数据  
✅ **先检查再执行** - 运行 `check_prerequisites.py`  
✅ **批量写入优化** - 每批最多 100 条记录

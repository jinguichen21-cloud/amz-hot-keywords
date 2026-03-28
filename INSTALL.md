# 商品热搜词技能包 - 安装指南

## 系统要求

- macOS 15.5+
- Python 3.9+
- Chrome 浏览器
- 钉钉客户端（用于访问 AI表格）

---

## 安装步骤

### Step 1: 安装 Python 依赖

```bash
cd /Users/kitano/.real/workspace/amazon_scraper_skill

# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖包
pip3 install selenium requests beautifulsoup4 pandas fake-useragent
```

### Step 2: 验证 mcporter CLI

```bash
# 检查 mcporter 是否已安装
mcporter --version

# 如果不包含，查看可用的 MCP 服务器
mcporter list
```

确保 `dingtalk` 服务器在列表中且状态健康。

### Step 3: 准备钉钉 AI表格

#### 3.1 创建表格

1. 打开钉钉客户端
2. 进入 **AI表格** 应用
3. 点击 **新建表格**
4. 添加以下字段（字段名必须完全一致）：

| 字段名 | 字段类型 | 配置说明 |
|--------|---------|----------|
| 搜索词 | 文本 | - |
| 本周排名 | 数字 | - |
| 上周排名 | 数字 | - |
| 涨跌幅度 | 单选 | 选项：上升、下降、持平 |

#### 3.2 获取表格 UUID

1. 打开刚创建的表格
2. 从 URL 中提取 Dentry UUID：
   ```
   https://dingtalk.com/base/.../<DENTRY_UUID>/...
                                      ^^^^^^^^^^^^
   ```
3. 复制 UUID（不含尖括号）

#### 3.3 获取 Sheet ID

1. 在表格页面点击右上角 **...**
2. 选择 **数据表信息**
3. 复制 **Sheet ID**

#### 3.4 获取 MCP URL

访问：https://mcp.dingtalk.com/

按照页面指引获取你的专属 MCP URL。

---

## Step 4: 首次运行配置

### 4.1 运行前置检查

```bash
cd /Users/kitano/.real/workspace/amazon_scraper_skill/scripts
python3 check_prerequisites.py
```

如果所有检查通过，继续下一步。

如果有检查未通过，根据提示修复问题。

### 4.2 交互式配置

首次运行爬虫脚本会自动引导你配置：

```bash
python3 amz123_enhanced_scraper_v2.py --keyword "dog bed"
```

按提示输入：
1. 搜索关键词（如 "dog bed"）
2. AI表格链接（完整 URL）
3. MCP URL（从 https://mcp.dingtalk.com/ 获取）
4. 热搜页面 URL（可选，默认使用 AMZ123 官方页面）

配置将保存到 `scraper_config.json`。

---

## Step 5: 验证安装

### 5.1 测试数据抓取

```bash
# 使用 --no-write 参数测试（仅抓取不写入）
python3 amz123_enhanced_scraper_v2.py --keyword "test" --no-write
```

检查输出：
- ✅ 成功打开浏览器
- ✅ 成功搜索关键词
- ✅ 成功提取数据（应有若干条记录）
- ✅ 生成 CSV 和 JSON 文件

### 5.2 测试数据写入

```bash
# 执行完整流程（抓取 + 写入）
python3 amz123_enhanced_scraper_v2.py --keyword "dog bed"
```

检查输出：
- ✅ 成功清空旧数据
- ✅ 成功分批写入新数据
- ✅ 钉钉表格中可见新数据

---

## 故障排查

### 问题 1：Python 版本过低

**症状：**
```
SyntaxError: invalid syntax
```

**解决方案：**
```bash
# 检查 Python 版本
python3 --version

# 如果低于 3.9，需要升级
brew upgrade python
```

### 问题 2：依赖包缺失

**症状：**
```
ModuleNotFoundError: No module named 'selenium'
```

**解决方案：**
```bash
pip3 install selenium requests beautifulsoup4 pandas fake-useragent
```

### 问题 3：mcporter 未找到

**症状：**
```
FileNotFoundError: [Errno 2] No such file or directory: 'mcporter'
```

**解决方案：**
- 确认已安装 Wukong/Real 应用
- 检查 PATH 环境变量是否包含 mcporter

### 问题 4：浏览器自动化失败

**症状：**
```
WebDriverException: Message: unknown error: cannot find Chrome binary
```

**解决方案：**
```bash
# 检查 Chrome 是否已安装
open -a "Google Chrome"

# 如果未安装，下载：
# https://www.google.com/chrome/
```

### 问题 5：MCP 连接失败

**症状：**
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**解决方案：**
1. 运行 `mcporter list` 检查服务器状态
2. 验证 MCP URL 配置正确
3. 访问 https://mcp.dingtalk.com/ 重新获取

---

## 卸载

如需卸载技能包：

```bash
# 删除技能包目录
rm -rf /Users/kitano/.real/workspace/amazon_scraper_skill

# 删除虚拟环境（如果创建了）
rm -rf /Users/kitano/.real/workspace/amazon_scraper_skill/.venv
```

---

## 更新

如需更新技能包到最新版本：

```bash
# 备份配置文件
cp /Users/kitano/.real/workspace/amazon_scraper_skill/scripts/scraper_config.json ~/Desktop/

# 删除旧版本
rm -rf /Users/kitano/.real/workspace/amazon_scraper_skill

# 重新安装（见上方安装步骤）
```

---

## 获取帮助

- 快速开始：[QUICK_START.md](./references/QUICK_START.md)
- 完整文档：[SKILL.md](./SKILL.md)
- 优化总结：[OPTIMIZATION_SUMMARY.md](./references/OPTIMIZATION_SUMMARY.md)

---

## 记住

✅ **先安装依赖** - 确保所有 Python 包已安装  
✅ **验证环境** - 运行 `check_prerequisites.py`  
✅ **配置凭证** - 准备好表格 UUID、Sheet ID、MCP URL  
✅ **测试模式** - 首次使用先用 `--no-write` 测试  

安装完成后，继续阅读 [QUICK_START.md](./references/QUICK_START.md) 开始使用！

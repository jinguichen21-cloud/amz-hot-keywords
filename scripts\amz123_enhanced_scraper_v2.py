#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMZ123 美国站热搜词数据抓取并写入指定钉钉AI表格（Selenium 增强版 v3）

核心改进：
1. 使用 Selenium 浏览器自动化抓取真实页面数据
2. 支持用户自定义关键词搜索（前 200 个搜索结果）
3. 自动计算涨跌幅度（上升/下降/持平）
4. 批量写入钉钉AI表格

使用方法：
    python3 amz123_selenium_scraper.py --keyword "dog bed" [--no-write] [--headless]
"""

import subprocess
import os
import json
import sys
from datetime import datetime
import time
import random
import pandas as pd
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# MCP 服务器配置参数
MCP_URL = "https://mcp-gw.dingtalk.com/server/6be847e8c4fdf5c6e63c4360059a8cf58401a916087628aeb4e4b7604d5185e2?key=b04323af19c7548d8e822fe564148b6a"

# 目标表格 UUID 和工作表 ID（从配置文件读取）
TARGET_TABLE_UUID = None
TARGET_SHEET_ID = None

# 配置文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "scraper_config.json")

# 默认配置
DEFAULT_CONFIG = {
    "keyword": "dog bed",
    "url": "https://www.amz123.com/usatopkeywords",
    "table_uuid": None,
    "sheet_id": None,
    "mcp_url": MCP_URL
}


def load_config():
    """加载用户配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
        except Exception as e:
            print(f"[警告] 读取配置文件失败：{e}，使用默认配置")
            return DEFAULT_CONFIG.copy()
    else:
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存用户配置文件"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[信息] 配置已保存到 {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"[错误] 保存配置文件失败：{e}")
        return False


def calculate_trend(current_rank, last_rank):
    """
    根据排名变化计算涨跌幅度
    
    规则：
    - 本周排名< 上周排名 → 上升（数字越小排名越靠前）
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


def setup_driver(headless=True):
    """设置 Chrome WebDriver"""
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        print("[信息] Chrome 浏览器启动成功")
        return driver
    except Exception as e:
        print(f"[错误] 启动浏览器失败：{e}")
        print("[提示] 请确保已安装 Chrome 浏览器和 ChromeDriver")
        return None


def extract_hot_words_with_selenium(driver, max_count=200):
    """
    使用 Selenium 从页面提取热搜词数据
    
    Args:
        driver: Selenium WebDriver
        max_count: 最大结果数
    
    Returns:
        list: 热搜词数据列表
    """
    # 等待搜索结果加载
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.table-body-item-words-word'))
        )
        print("[信息] 搜索结果已加载")
    except TimeoutException:
        print("[警告] 等待搜索结果超时，尝试继续抓取...")
        time.sleep(3)
    
    # 使用 JavaScript 提取数据-根据实际页面结构调整
    script = f"""
    // 找到所有热词项的父容器
    const items = Array.from(document.querySelectorAll('.table-body-item'));
    
    return items.slice(0, {max_count}).map(item => {{
      // 提取搜索词
      const wordElem = item.querySelector('.table-body-item-words-word');
      const word = wordElem ? wordElem.textContent.trim() : '';
      
      // 提取排名数据
      const rankContainer = item.querySelector('.table-body-item-rank');
      let currentRank = 0;
      let lastRank = 0;
      
      if (rankContainer) {{
        const spans = rankContainer.querySelectorAll('span');
        if (spans.length >= 2) {{
          const currentText = spans[0].textContent.trim();
          const lastText = spans[1].textContent.trim();
          //只有当文本是数字时才解析
          currentRank = /^\\d+$/.test(currentText) ? parseInt(currentText) : 0;
          lastRank = /^\\d+$/.test(lastText) ? parseInt(lastText) : 0;
        }}
      }}
      
      return {{
        word: word,
        currentRank: currentRank,
        lastRank: lastRank
      }};
    }});
    """
    
    data = driver.execute_script(script)
    
    # 过滤空词和无效数据
    filtered_data = [item for item in data if item['word'] and len(item['word']) > 0]
    
    return filtered_data


def search_keyword_in_amz123(driver, base_url, keyword, max_results=200):
    """
    在 AMZ123 中搜索关键词并抓取数据
    
    Args:
        driver: Selenium WebDriver
        base_url: 基础 URL
        keyword: 搜索关键词
        max_results: 最大结果数
    
    Returns:
        list: 热搜词数据列表
    """
    print(f"[信息] 正在搜索与 '{keyword}' 相关的关键词...")
    
    # 构建搜索 URL
    search_url = f"{base_url}?search={keyword}"
    
    print(f"[信息] 访问搜索页面：{search_url}")
    driver.get(search_url)
    
    # 等待页面加载
    time.sleep(5)
    
    # 保存完整页面 HTML 用于分析
    page_source = driver.page_source
    output_file = os.path.join(SCRIPT_DIR, "amz123_debug_page.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(page_source)
    print(f"[信息] 已保存页面内容到 {output_file} 供分析")
    
    # 尝试多种可能的 CSS 选择器
    selectors_to_try = [
        '.table-body-item',
        '.hotword-item',
        '.keyword-item',
        '[class*="item"]',
        'tr',
        '.list-item'
    ]
    
    for selector in selectors_to_try:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"[信息] 找到匹配的选择器：{selector} (共 {len(elements)} 个元素)")
        except Exception as e:
            continue
    
    # 提取数据
    keywords_data = extract_hot_words_with_selenium(driver, max_results)
    
    if not keywords_data:
        print("[警告] 未能从页面提取到数据，尝试滚动页面...")
        # 尝试滚动页面以加载更多数据
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        keywords_data = extract_hot_words_with_selenium(driver, max_results)
    
    print(f"[成功] 搜索完成，共找到 {len(keywords_data)} 个相关关键词")
    return keywords_data


def scrape_hot_keywords_direct(driver, url):
    """
    直接抓取热搜榜单数据（无关键词搜索）
    
    Args:
        driver: Selenium WebDriver
        url: 热搜页面 URL
    
    Returns:
        list: 热搜词数据列表
    """
    print(f"[信息] 正在访问页面：{url}")
    driver.get(url)
    
    # 等待页面加载
    time.sleep(3)
    
    # 提取数据
    keywords_data = extract_hot_words_with_selenium(driver, 200)
    
    if not keywords_data:
        print("[警告] 未能从页面提取到关键词信息")
        return []
    
    print(f"[成功] 成功提取到 {len(keywords_data)} 个关键词信息")
    return keywords_data


def format_data_for_table(raw_data):
    """
    格式化数据以匹配钉钉表格字段
    
    Args:
        raw_data: 原始数据列表
    
    Returns:
        list: 格式化后的数据
    """
    formatted_data = []
    for item in raw_data:
        formatted_data.append({
            "搜索词": item['word'],
            "本周排名": item['currentRank'],
            "上周排名": item['lastRank'],
            "涨跌幅度": calculate_trend(item['currentRank'], item['lastRank'])
        })
    return formatted_data


def save_to_csv(data, filename=None):
    """将数据保存到 CSV 文件"""
    if not data:
        print("[错误] 没有数据可保存")
        return None
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SCRIPT_DIR, f"amz123_hotwords_{timestamp}.csv")
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"[成功] 数据已保存到 {filename}")
    return filename


def add_records_to_dingtalk_table(records, table_uuid, sheet_id, mcp_url):
    """向钉钉AI表格添加记录"""
    try:
        env = os.environ.copy()
        env["DINGTALK_MCP_URL"] = mcp_url
        
        args = {
            "dentryUuid": table_uuid,
            "sheetIdOrName": sheet_id,
            "records": records
        }
        
        args_json = json.dumps(args, ensure_ascii=False)
        
        cmd = ["mcporter", "call", "dingtalk-ai-table", "add_base_record", "--args", args_json, "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
        data = json.loads(result.stdout)
        
        if data.get("success"):
            print(f"[成功] 成功添加 {len(records)} 条记录到 AI表格")
            return True
        else:
            print(f"[错误] 添加记录失败：{data.get('info', 'Unknown error')}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"[错误] 添加记录失败：{e}")
        if e.stderr:
            print(f"错误输出：{e.stderr}")
        return False
    except FileNotFoundError:
        print("[错误] 未找到 mcporter 命令，请确保已正确安装")
        return False
    except Exception as e:
        print(f"[错误] 添加记录时发生未知错误：{e}")
        return False


def clear_table_records(table_uuid, sheet_id, mcp_url):
    """清空表格中的所有记录"""
    try:
        env = os.environ.copy()
        env["DINGTALK_MCP_URL"] = mcp_url
        
        # 查询所有记录
        args = {
            "dentryUuid": table_uuid,
            "sheetIdOrName": sheet_id,
            "maxRecords": 1000
        }
        
        args_json = json.dumps(args, ensure_ascii=False)
        cmd = ["mcporter", "call", "dingtalk-ai-table", "query_base_record", "--args", args_json, "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
        data = json.loads(result.stdout)
        
        if data.get("success"):
            records = data.get("info", {}).get("records", [])
            record_ids = [r.get("id") for r in records if r.get("id")]
            
            if record_ids:
                # 删除记录
                delete_args = {
                    "dentryUuid": table_uuid,
                    "sheetIdOrName": sheet_id,
                    "recordIds": record_ids
                }
                
                delete_json = json.dumps(delete_args, ensure_ascii=False)
                cmd = ["mcporter", "call", "dingtalk-ai-table", "delete_base_record", "--args", delete_json, "--output", "json"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
                data = json.loads(result.stdout)
                
                if data.get("success"):
                    print(f"[成功] 成功清空 {len(record_ids)} 条旧记录")
                    return True
        
        return False
    except Exception as e:
        print(f"[错误] 清空表格失败：{e}")
        return False


def write_to_dingtalk_table(data, table_uuid, sheet_id, mcp_url, clear_first=True):
    """将数据写入钉钉AI表格"""
    print(f"[信息] 开始向钉钉AI表格写入数据...")
    print(f"[信息] 表格 UUID: {table_uuid}")
    print(f"[信息] 工作表 ID: {sheet_id}")
    
    if clear_first:
        print("[信息] 正在清空旧数据...")
        clear_table_records(table_uuid, sheet_id, mcp_url)
        time.sleep(2)
    
    # 转换为 MCP 格式
    records = []
    for item in data:
        record_fields = {
            "搜索词": item["搜索词"],
            "本周排名": str(item["本周排名"]),
            "上周排名": str(item["上周排名"]),
            "涨跌幅度": item["涨跌幅度"]
        }
        records.append({"fields": record_fields})
    
    batch_size = 20
    total_records = len(records)
    
    print(f"[信息] 开始分批写入 {total_records} 条记录，每批 {batch_size} 条")
    
    success_count = 0
    for i in range(0, total_records, batch_size):
        batch = records[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total_records + batch_size - 1) // batch_size
        
        print(f"[信息] 写入第 {batch_num}/{total_batches} 批记录 ({len(batch)} 条)")
        
        if add_records_to_dingtalk_table(batch, table_uuid, sheet_id, mcp_url):
            success_count += len(batch)
            print(f"[成功] 第 {batch_num} 批记录写入成功")
        else:
            print(f"[失败] 第 {batch_num} 批记录写入失败")
        
        time.sleep(2)
    
    print(f"[完成] 数据写入完成，成功写入 {success_count}/{total_records} 条记录")
    return success_count > 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AMZ123 热搜词数据抓取工具（Selenium 增强版 v3）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 amz123_selenium_scraper.py --keyword "dog bed"
  python3 amz123_selenium_scraper.py --keyword "yoga mat" --no-write
  python3 amz123_selenium_scraper.py --keyword "pet supplies" --headless=false
        """
    )
    parser.add_argument("--keyword", type=str, required=True, help="搜索关键词（例如：'dog bed'）")
    parser.add_argument("--no-write", action="store_true", help="仅抓取数据，不写入钉钉表格")
    parser.add_argument("--headless", type=str, default="true", help="是否使用无头模式 (true/false)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("AMZ123 美国站热搜词数据抓取工具（Selenium 增强版 v3）")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    
    # 更新关键词
    keyword = args.keyword.strip()
    print(f"\n[信息] 搜索关键词：'{keyword}'")
    print(f"[信息] 使用 URL: {config['url']}")
    
    # 解析 headless 参数
    headless = args.headless.lower() == 'true'
    
    # 设置浏览器驱动
    driver = setup_driver(headless)
    if not driver:
        print("\n[错误] 无法启动浏览器，请检查 Chrome 和 ChromeDriver 是否正确安装")
        return 1
    
    try:
        # 抓取数据
        print("\n" + "=" * 60)
        print("开始抓取数据...")
        print("=" * 60)
        
        raw_data = search_keyword_in_amz123(driver, config['url'], keyword, max_results=200)
        
        if not raw_data:
            print("\n[错误] 未能获取到任何数据")
            return 1
        
        # 格式化数据
        formatted_data = format_data_for_table(raw_data)
        
        # 保存 CSV
        csv_file = save_to_csv(formatted_data)
        
        # 如果不写入，到此结束
        if args.no_write:
            print("\n[信息] 已启用 --no-write 模式，跳过写入步骤")
            print(f"[信息] 数据已保存到：{csv_file}")
            return 0
        
        # 检查表格配置
        if not config.get('table_uuid') or not config.get('sheet_id'):
            print("\n[错误] 缺少表格配置 (table_uuid 或 sheet_id)")
            print("[提示] 请在配置文件中添加有效的表格凭证")
            return 1
        
        # 写入钉钉表格
        print("\n" + "=" * 60)
        print("开始写入钉钉表格...")
        print("=" * 60)
        
        success = write_to_dingtalk_table(
            formatted_data,
            config['table_uuid'],
            config['sheet_id'],
            config['mcp_url']
        )
        
        if success:
            print("\n" + "=" * 60)
            print("[成功] 任务完成！")
            print("=" * 60)
            return 0
        else:
            print("\n[警告] 写入部分失败，请检查日志")
            return 1
    
    except Exception as e:
        print(f"\n[错误] 执行过程中发生异常：{e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # 关闭浏览器
        if driver:
            print("\n[信息] 关闭浏览器...")
            driver.quit()


if __name__ == '__main__':
    sys.exit(main())

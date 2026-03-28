#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前置条件检查脚本 - 验证技能执行环境是否就绪

Checks:
1. Python version (3.9+)
2. Required dependencies installed
3. Configuration file exists and is valid
4. DingTalk MCP connection available
5. AI Table fields match expected structure
"""

import sys
import json
import os
import subprocess
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_check(name, passed, message=None):
    """Print check result with color"""
    status = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
    print(f"{status} {name}")
    if message:
        color = Colors.GREEN if passed else Colors.RED
        print(f"  {color}{message}{Colors.END}")

def check_python_version():
    """Check Python version >= 3.9"""
    version = sys.version_info
    passed = version.major >= 3 and version.minor >= 9
    message = f"Python {version.major}.{version.minor}.{version.micro}"
    print_check("Python 版本 (>= 3.9)", passed, message)
    return passed

def check_dependencies():
    """Check required Python packages"""
    required = ['selenium', 'requests']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if not missing:
        print_check("Python 依赖包", True, f"已安装：{', '.join(required)}")
        return True
    else:
        print_check("Python 依赖包", False, f"缺失：{', '.join(missing)}")
        print(f"  安装命令：pip3 install {' '.join(missing)}")
        return False

def check_config_file():
    """Check configuration file exists and is valid"""
    config_paths = [
        Path(__file__).parent / 'scraper_config.json',
        Path('/Users/kitano/.real/workspace/amazon_scraper/scraper_config.json')
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                required_fields = ['keyword', 'url', 'table_uuid', 'sheet_id', 'mcp_url']
                missing_fields = [f for f in required_fields if f not in config]
                
                if not missing_fields:
                    print_check("配置文件", True, f"位于：{config_path}")
                    return True, config
                else:
                    print_check("配置文件", False, f"缺少字段：{', '.join(missing_fields)}")
                    return False, None
            except json.JSONDecodeError as e:
                print_check("配置文件", False, f"JSON 格式错误：{e}")
                return False, None
    
    print_check("配置文件", False, "未找到 scraper_config.json")
    print(f"  首次运行时将自动创建配置文件")
    return False, None

def check_mcp_connection():
    """Check DingTalk MCP connection"""
    try:
        # 先尝试使用 real_cli 工具检查
        result = subprocess.run(
            ['mcporter', 'list'],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, 'PATH': '/usr/local/bin:/opt/homebrew/bin:' + os.environ.get('PATH', '')}
        )
        
        if result.returncode == 0:
            has_dingtalk = 'dingtalk' in result.stdout.lower()
            if has_dingtalk:
                print_check("钉钉 MCP 连接", True, "服务器状态：健康")
                return True
            else:
                print_check("钉钉 MCP 连接", False, "未找到 dingtalk 服务器")
                print(f"  提示：请确保已配置钉钉 MCP 服务器")
                return False
        else:
            print_check("钉钉 MCP 连接", False, f"命令执行失败 (返回码：{result.returncode})")
            print(f"  提示：首次运行时可跳过此项，配置完成后自动验证")
            return None  # 返回 None 表示不确定
    except FileNotFoundError:
        print_check("钉钉 MCP 连接", False, "未找到 mcporter 命令")
        print(f"  提示：请确保已安装 Wukong/Real 应用")
        return None
    except subprocess.TimeoutExpired:
        print_check("钉钉 MCP 连接", False, "连接超时")
        return False
    except PermissionError as e:
        print_check("钉钉 MCP 连接", False, f"权限受限：{e}")
        print(f"  提示：首次运行时可跳过此项")
        return None
    except Exception as e:
        print_check("钉钉 MCP 连接", False, f"检查失败：{e}")
        return None

def check_table_fields(config):
    """Check AI Table field structure matches expected format"""
    if not config:
        return False
    
    dentry_uuid = config.get('table_uuid')
    sheet_id = config.get('sheet_id')
    mcp_url = config.get('mcp_url')
    
    if not all([dentry_uuid, sheet_id, mcp_url]):
        print_check("AI表格字段检查", False, "配置信息不完整")
        print(f"  提示：首次运行时请确保配置文件中包含 table_uuid, sheet_id, mcp_url")
        return None
    
    try:
        # List table fields
        cmd = [
            'mcporter', 'call', 'dingtalk.list_base_field',
            f'dentryUuid={dentry_uuid}',
            f'sheetIdOrName={sheet_id}'
        ]
        
        env = os.environ.copy()
        env['DINGTALK_MCP_URL'] = mcp_url
        env['PATH'] = '/usr/local/bin:/opt/homebrew/bin:' + env.get('PATH', '')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            env=env
        )
        
        if result.returncode == 0:
            fields_data = json.loads(result.stdout)
            field_names = [f.get('name', '') for f in fields_data] if isinstance(fields_data, list) else []
            
            required_fields = ['搜索词', '本周排名', '上周排名', '涨跌幅度']
            missing_fields = [f for f in required_fields if f not in field_names]
            
            if not missing_fields:
                print_check("AI表格字段结构", True, f"包含所有必需字段")
                return True
            else:
                print_check("AI表格字段结构", False, f"缺少字段：{', '.join(missing_fields)}")
                print(f"  当前字段：{', '.join(field_names)}")
                print(f"  请在表格中添加缺失的字段")
                return False
        else:
            print_check("AI表格字段检查", False, f"获取字段失败 (返回码：{result.returncode})")
            print(f"  提示：首次运行时可跳过此项，配置完成后自动验证")
            return None
            
    except json.JSONDecodeError:
        print_check("AI表格字段检查", False, "响应格式错误")
        return None
    except subprocess.TimeoutExpired:
        print_check("AI表格字段检查", False, "请求超时")
        return None
    except PermissionError as e:
        print_check("AI表格字段检查", False, f"权限受限：{e}")
        print(f"  提示：首次运行时可跳过此项")
        return None
    except Exception as e:
        print_check("AI表格字段检查", False, f"检查失败：{e}")
        print(f"  提示：首次运行时请确保配置正确")
        return None

def main():
    """Main check function"""
    print(f"\n{Colors.BOLD}=== 商品热搜词技能 - 前置条件检查 ==={Colors.END}\n")
    
    checks = []
    
    # Run basic checks
    checks.append(check_python_version())
    checks.append(check_dependencies())
    
    # Check configuration
    config_ok, config = check_config_file()
    checks.append(config_ok)
    
    # If config exists, check MCP and table
    if config_ok:
        checks.append(check_mcp_connection())
        checks.append(check_table_fields(config))
    
    # Summary
    print(f"\n{'='*50}")
    passed = sum(1 for c in checks if c is True)
    failed = sum(1 for c in checks if c is False)
    skipped = sum(1 for c in checks if c is None)
    total = len(checks)
    
    if failed == 0:
        print(f"{Colors.GREEN}✓ 所有必需检查通过 ({passed}/{total}){Colors.END}")
        if skipped > 0:
            print(f"{Colors.YELLOW}  跳过 {skipped} 项（首次运行可忽略）{Colors.END}")
        print(f"\n{Colors.BLUE}可以开始执行技能了！{Colors.END}")
        print(f"\n运行命令:")
        print(f"  python3 amz123_enhanced_scraper_v2.py --keyword \"<你的关键词>\"")
        return 0
    else:
        print(f"{Colors.RED}✗ {failed} 项检查未通过 ({passed}/{total}){Colors.END}")
        if skipped > 0:
            print(f"{Colors.YELLOW}  跳过 {skipped} 项{Colors.END}")
        print(f"\n请先解决上述问题后再执行技能")
        return 1

if __name__ == '__main__':
    sys.exit(main())

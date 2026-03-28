#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置文件管理功能
Test Configuration Management Module
"""

import unittest
import json
import os
import sys
import tempfile
import shutil

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# Import from the scraper script
from amz123_enhanced_scraper_v2 import load_config, save_config, DEFAULT_CONFIG, CONFIG_FILE


class ConfigTests(unittest.TestCase):
    """配置文件管理测试"""
    
    def setUp(self):
        """每个测试前的准备工作"""
        # Backup original config if exists
        self.original_config = None
        self.backup_path = None
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.test_dir, 'scraper_config.json')
        
        if os.path.exists(CONFIG_FILE):
            self.backup_path = CONFIG_FILE + '.bak'
            shutil.copy(CONFIG_FILE, self.backup_path)
    
    def tearDown(self):
        """每个测试后的清理工作"""
        # Restore original config
        if self.backup_path and os.path.exists(self.backup_path):
            shutil.move(self.backup_path, CONFIG_FILE)
        
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_load_default_config(self):
        """测试加载默认配置"""
        # Temporarily rename config file
        temp_config = CONFIG_FILE + '.temp'
        if os.path.exists(CONFIG_FILE):
            shutil.move(CONFIG_FILE, temp_config)
        
        try:
            config = load_config()
            self.assertIn('keyword', config)
            self.assertEqual(config['keyword'], 'dog bed')
            self.assertEqual(config['url'], 'https://www.amz123.com/usatopkeywords')
        finally:
            # Restore
            if os.path.exists(temp_config):
                shutil.move(temp_config, CONFIG_FILE)
    
    def test_save_config_success(self):
        """测试保存配置成功"""
        test_config = {
            'keyword': 'test keyword',
            'url': 'https://test.example.com',
            'table_uuid': 'test123uuid',
            'sheet_id': 'abc123',
            'mcp_url': 'https://mcp.test.com'
        }
        
        result = save_config(test_config)
        self.assertTrue(result)
        
        # Verify file was created and content is correct
        self.assertTrue(os.path.exists(CONFIG_FILE))
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config['keyword'], 'test keyword')
        self.assertEqual(saved_config['url'], 'https://test.example.com')
    
    def test_load_existing_config(self):
        """测试加载现有配置"""
        # Create a test config file
        test_config = {
            'keyword': 'custom keyword',
            'url': 'https://custom.example.com',
            'table_uuid': 'custom123',
            'sheet_id': 'xyz789',
            'mcp_url': 'https://mcp.custom.com'
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
        
        loaded = load_config()
        self.assertEqual(loaded['keyword'], 'custom keyword')
        self.assertEqual(loaded['url'], 'https://custom.example.com')
    
    def test_load_invalid_json_config(self):
        """测试加载格式错误的 JSON 配置"""
        # Write invalid JSON
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write('{invalid json content')
        
        # Should fall back to default config without crashing
        config = load_config()
        self.assertIsInstance(config, dict)
        # Should have default values or merged values
        self.assertIn('keyword', config)
    
    def test_config_merge_with_defaults(self):
        """测试配置与默认值的合并"""
        # Create partial config
        partial_config = {
            'keyword': 'partial'
            # Missing other fields
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(partial_config, f, ensure_ascii=False, indent=2)
        
        loaded = load_config()
        # Should have the custom keyword
        self.assertEqual(loaded['keyword'], 'partial')
        # Should have default url
        self.assertEqual(loaded['url'], 'https://www.amz123.com/usatopkeywords')
    
    def test_config_persistence_after_update(self):
        """测试配置更新后的持久化"""
        # Initial config
        config1 = {
            'keyword': 'first',
            'url': 'https://first.com',
            'table_uuid': 'uuid1',
            'sheet_id': 'sheet1',
            'mcp_url': 'https://mcp1.com'
        }
        save_config(config1)
        
        # Update config
        config2 = {
            'keyword': 'second',
            'url': 'https://second.com',
            'table_uuid': 'uuid1',
            'sheet_id': 'sheet1',
            'mcp_url': 'https://mcp1.com'
        }
        save_config(config2)
        
        # Load and verify
        loaded = load_config()
        self.assertEqual(loaded['keyword'], 'second')
        self.assertEqual(loaded['url'], 'https://second.com')


if __name__ == '__main__':
    unittest.main(verbosity=2)

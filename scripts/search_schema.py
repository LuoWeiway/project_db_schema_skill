#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字段搜索功能 - 搜索包含指定关键字的表和字段
"""

import json
import sys
import os

def load_config():
    """加载配置"""
    config_file = '.claude/db-schema/config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def search_schema(keyword):
    """搜索表结构"""
    keyword = keyword.lower()

    # 检查数据文件是否存在
    summary_file = '.claude/db-schema/summary_data.json'
    if not os.path.exists(summary_file):
        print("错误: 未找到表结构数据，请先运行 read-all")
        return

    # 读取汇总数据
    with open(summary_file, 'r', encoding='utf-8') as f:
        tables = json.load(f)

    # 搜索表名
    matched_tables = [t for t in tables if keyword in t['name'].lower()]

    # 搜索字段
    matched_fields = []
    for table in tables:
        table_file = f".claude/db-schema/tables/{table['name']}.md"
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                for line in lines:
                    if '|' in line and keyword in line.lower():
                        # 提取字段信息
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 6 and parts[1] and parts[1] != '字段':
                            matched_fields.append({
                                'table': table['name'],
                                'field': parts[1],
                                'type': parts[2],
                                'comment': parts[5] if len(parts) > 5 else '-'
                            })
        except:
            pass

    # 输出结果
    print("=" * 50)
    print(f"搜索关键字: {keyword}")
    print("=" * 50)

    if matched_tables:
        print(f"\n表名匹配: {len(matched_tables)} 个")
        for t in matched_tables[:10]:
            print(f"  - {t['name']}: {t['comment']}")

    if matched_fields:
        print(f"\n字段匹配: {len(matched_fields)} 个")
        print("| 表名 | 字段 | 类型 | 说明 |")
        print("|------|------|------|------|")
        for f in matched_fields[:30]:
            print(f"| {f['table']} | {f['field']} | {f['type']} | {f['comment']} |")

    if not matched_tables and not matched_fields:
        print("未找到匹配的表或字段")

    # 推测关联关系
    if matched_fields and keyword.endswith('_id'):
        ref_table = 't_' + keyword[:-3] if not keyword.startswith('t_') else keyword[:-3]
        print(f"\n推测关联:")
        for f in matched_fields[:10]:
            print(f"  - {f['table']}.{f['field']} -> {ref_table}.id")

if __name__ == '__main__':
    keyword = sys.argv[1] if len(sys.argv) > 1 else ''
    if not keyword:
        print("用法: python search_schema.py <关键字>")
        sys.exit(1)
    search_schema(keyword)
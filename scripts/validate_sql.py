#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL验证功能 - 验证SQL字段是否存在，检测NOT NULL误用
"""

import re
import json
import sys
import os

def validate_sql(sql_file):
    """验证SQL文件"""

    # 读取表结构数据
    summary_file = '.claude/db-schema/summary_data.json'
    if not os.path.exists(summary_file):
        print("错误: 未找到表结构数据，请先运行 read-all")
        return

    with open(summary_file, 'r', encoding='utf-8') as f:
        tables_data = json.load(f)

    tables = {t['name']: t for t in tables_data}

    # 读取 SQL 文件
    if not os.path.exists(sql_file):
        print(f"错误: 文件不存在 {sql_file}")
        return

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    errors = []
    warnings = []

    # 提取表名（FROM, JOIN 后面的表名）
    table_pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    tables_in_sql = re.findall(table_pattern, sql_content, re.IGNORECASE)

    # 验证表是否存在
    for table in set(tables_in_sql):
        table_lower = table.lower()
        if table_lower not in tables:
            errors.append({
                'type': '表不存在',
                'table': table,
                'message': f"表 {table} 不存在于数据库中"
            })

    # 检查 NOT NULL 字段是否误用 IS NOT NULL
    for table in set(tables_in_sql):
        table_lower = table.lower()
        if table_lower not in tables:
            continue

        # 读取表结构文档
        table_file = f".claude/db-schema/tables/{table_lower}.md"
        if not os.path.exists(table_file):
            continue

        with open(table_file, 'r', encoding='utf-8') as f:
            table_content = f.read()

        # 提取 NOT NULL 字段
        # 格式: | field_name | type | N | ... | (N 表示 NOT NULL)
        not_null_pattern = r'\|\s*(\w+)\s*\|\s*\w+\s*\|\s*N\s*\|'
        not_null_fields = re.findall(not_null_pattern, table_content)

        for field in not_null_fields:
            # 检查是否误用 IS NOT NULL
            pattern = rf'\b{field}\s+IS\s+NOT\s+NULL\b'
            if re.search(pattern, sql_content, re.IGNORECASE):
                warnings.append({
                    'type': 'NOT NULL误用',
                    'table': table,
                    'field': field,
                    'message': f"{table}.{field} 定义为 NOT NULL，无需 IS NOT NULL 判断"
                })

    # 输出验证结果
    print("=" * 60)
    print(f"SQL 验证报告: {sql_file}")
    print("=" * 60)

    if errors:
        print(f"\n错误 ({len(errors)} 个):")
        for e in errors:
            print(f"  [X] {e['type']}: {e['message']}")

    if warnings:
        print(f"\n警告 ({len(warnings)} 个):")
        for w in warnings:
            print(f"  [!] {w['type']}: {w['message']}")

    if not errors and not warnings:
        print("\n验证通过，未发现问题")

    print(f"\n统计:")
    print(f"  - 涉及表: {len(set(tables_in_sql))} 个")
    print(f"  - 错误: {len(errors)} 个")
    print(f"  - 警告: {len(warnings)} 个")

    return len(errors) == 0

if __name__ == '__main__':
    sql_file = sys.argv[1] if len(sys.argv) > 1 else ''
    if not sql_file:
        print("用法: python validate_sql.py <SQL文件路径>")
        sys.exit(1)
    validate_sql(sql_file)
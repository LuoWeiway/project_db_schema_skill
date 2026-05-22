#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
表关联分析功能 - 分析外键关系和命名约定
"""

import json
import os
from collections import defaultdict

def load_config():
    """加载配置"""
    config_file = '.claude/db-schema/config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def analyze_relations():
    """分析表关联关系"""
    config = load_config()
    if not config:
        print("错误: 未找到配置文件，请先运行 init")
        return

    try:
        import pymysql
    except ImportError:
        print("错误: 需要安装 PyMySQL: pip install pymysql")
        return

    print("正在连接数据库...")
    conn = pymysql.connect(
        host=config['host'],
        port=config.get('port', 3306),
        user=config['user'],
        password=config['password'],
        database=config['database'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()

    # 1. 查询外键关系
    print("\n1. 查询外键约束...")
    cursor.execute("""
        SELECT
            TABLE_NAME, COLUMN_NAME,
            REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    foreign_keys = cursor.fetchall()
    print(f"   找到 {len(foreign_keys)} 个外键约束")

    # 2. 分析命名约定（xxx_id 字段）
    print("\n2. 分析命名约定（xxx_id 字段）...")
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND COLUMN_NAME LIKE '%_id'
          AND COLUMN_NAME != 'id'
        ORDER BY TABLE_NAME, COLUMN_NAME
    """)
    id_columns = cursor.fetchall()
    print(f"   找到 {len(id_columns)} 个 _id 字段")

    # 推测关联关系
    relations = defaultdict(list)
    for table, column, comment in id_columns:
        # 推测主表名
        ref_table = column[:-3]  # 去掉 _id
        if not ref_table.startswith('t_'):
            ref_table = 't_' + ref_table
        relations[table].append({
            'column': column,
            'ref_table': ref_table,
            'ref_column': 'id',
            'type': '推测',
            'comment': comment
        })

    # 3. 生成关联关系文档
    print("\n3. 生成关联关系文档...")

    doc_content = "# 表关联关系\n\n"
    doc_content += f"生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}\n\n"
    doc_content += f"统计: 外键约束 {len(foreign_keys)} 个, 推测关联 {len(id_columns)} 个\n\n"

    # 外键约束部分
    doc_content += "## 外键约束\n\n"
    if foreign_keys:
        doc_content += "| 从表 | 字段 | 主表 | 主键 |\n"
        doc_content += "|------|------|------|------|\n"
        for fk in foreign_keys:
            doc_content += f"| {fk[0]} | {fk[1]} | {fk[2]} | {fk[3]} |\n"
    else:
        doc_content += "无外键约束\n"

    # 推测关联部分
    doc_content += "\n## 推测关联（基于命名约定）\n\n"
    doc_content += "> 以下关联基于 `xxx_id` 命名约定推测，需人工确认\n\n"

    for table, refs in sorted(relations.items()):
        doc_content += f"### {table}\n\n"
        for ref in refs:
            doc_content += f"- {ref['column']} -> {ref['ref_table']}.{ref['ref_column']}"
            if ref['comment']:
                doc_content += f" ({ref['comment']})"
            doc_content += "\n"
        doc_content += "\n"

    # 保存文档
    os.makedirs('.claude/db-schema', exist_ok=True)
    with open('.claude/db-schema/relations.md', 'w', encoding='utf-8') as f:
        f.write(doc_content)

    # 保存结构化数据
    relations_data = {
        'foreign_keys': [
            {
                'from_table': fk[0],
                'from_column': fk[1],
                'to_table': fk[2],
                'to_column': fk[3]
            } for fk in foreign_keys
        ],
        'inferred_relations': {
            table: refs for table, refs in relations.items()
        }
    }

    with open('.claude/db-schema/relations_data.json', 'w', encoding='utf-8') as f:
        json.dump(relations_data, f, ensure_ascii=False, indent=2)

    print(f"\n完成! 已生成:")
    print(f"  - .claude/db-schema/relations.md")
    print(f"  - .claude/db-schema/relations_data.json")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    analyze_relations()
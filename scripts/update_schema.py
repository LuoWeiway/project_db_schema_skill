#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增量更新功能 - 检测并更新有变化的表结构
"""

import json
import os
from datetime import datetime

def load_config():
    """加载配置"""
    config_file = '.claude/db-schema/config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_table_structure(cursor, table_name):
    """获取单个表的结构"""

    # 查询字段信息
    cursor.execute("""
        SELECT
            COLUMN_NAME,
            COLUMN_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COLUMN_COMMENT,
            COLUMN_KEY
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """, (table_name,))
    columns = cursor.fetchall()

    # 查询索引
    cursor.execute("SHOW INDEX FROM `%s`" % table_name)
    indexes = cursor.fetchall()

    # 查询表信息
    cursor.execute("""
        SELECT TABLE_COMMENT, ENGINE, TABLE_ROWS
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
    """, (table_name,))
    table_info = cursor.fetchone()

    return columns, indexes, table_info

def generate_table_doc(table_name, columns, indexes, table_info):
    """生成表结构文档"""

    comment = table_info[0] if table_info else ''
    engine = table_info[1] if table_info else 'InnoDB'
    rows = table_info[2] if table_info else 0

    doc = f"# {table_name}"
    if comment:
        doc += f" — {comment}"
    doc += "\n\n"

    doc += "## 基本信息\n"
    doc += f"- **表名**: {table_name}\n"
    if comment:
        doc += f"- **说明**: {comment}\n"
    doc += f"- **引擎**: {engine}\n"
    doc += f"- **预估行数**: ~{rows}\n\n"

    doc += "## 字段清单\n\n"
    doc += "| 字段 | 类型 | 可空 | 默认值 | 说明 |\n"
    doc += "|------|------|------|--------|------|\n"

    for col in columns:
        field, col_type, nullable, default, col_comment, key = col
        nullable_str = 'N' if nullable == 'NO' else 'Y'
        default_str = str(default) if default else '-'
        if default_str == 'CURRENT_TIMESTAMP':
            default_str = 'NOW'
        comment_str = col_comment if col_comment else '-'
        doc += f"| {field} | {col_type} | {nullable_str} | {default_str} | {comment_str} |\n"

    # 索引部分
    if indexes:
        doc += "\n## 索引\n\n"
        doc += "| 名称 | 类型 | 字段 |\n"
        doc += "|------|------|------|\n"

        seen_indexes = set()
        for idx in indexes:
            idx_name = idx[2]
            if idx_name in seen_indexes:
                continue
            seen_indexes.add(idx_name)

            idx_type = 'PK' if idx_name == 'PRIMARY' else ('UNI' if idx[1] == 0 else 'IDX')
            idx_cols = idx[4]
            doc += f"| {idx_name} | {idx_type} | {idx_cols} |\n"

    return doc

def update_tables(tables_to_update=None):
    """增量更新表结构"""

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

    # 获取所有表
    cursor.execute("""
        SELECT TABLE_NAME, UPDATE_TIME, TABLE_COMMENT
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
    """)
    db_tables = cursor.fetchall()

    # 检测需要更新的表
    changed_tables = []
    for table_name, update_time, table_comment in db_tables:
        table_file = f".claude/db-schema/tables/{table_name}.md"

        if tables_to_update and table_name not in tables_to_update:
            continue

        if not os.path.exists(table_file):
            changed_tables.append((table_name, '新增', table_comment))
        elif update_time and str(update_time) > config.get('last_update', ''):
            changed_tables.append((table_name, '更新', table_comment))

    if not changed_tables:
        print("\n没有需要更新的表")
        cursor.close()
        conn.close()
        return

    print(f"\n检测到 {len(changed_tables)} 个表需要更新:")
    for table, reason, comment in changed_tables[:20]:
        print(f"  - {table}: {reason} ({comment})")

    if len(changed_tables) > 20:
        print(f"  ... 还有 {len(changed_tables) - 20} 个表")

    # 更新表结构
    print("\n开始更新...")
    updated_count = 0

    os.makedirs('.claude/db-schema/tables', exist_ok=True)

    for table_name, reason, _ in changed_tables:
        try:
            columns, indexes, table_info = get_table_structure(cursor, table_name)
            doc = generate_table_doc(table_name, columns, indexes, table_info)

            table_file = f".claude/db-schema/tables/{table_name}.md"
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(doc)

            updated_count += 1
            print(f"  [{updated_count}/{len(changed_tables)}] {table_name} - {reason}")
        except Exception as e:
            print(f"  [错误] {table_name}: {e}")

    # 更新配置
    config['last_update'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    config['table_count'] = len(db_tables)

    with open('.claude/db-schema/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\n完成! 更新了 {updated_count} 个表")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    import sys
    tables = sys.argv[1:] if len(sys.argv) > 1 else None
    update_tables(tables)
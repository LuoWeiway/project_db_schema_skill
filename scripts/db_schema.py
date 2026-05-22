#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
db-schema 命令行工具
统一入口，支持所有功能

用法:
    python db_schema.py                  # 显示帮助
    python db_schema.py init             # 初始化配置
    python db_schema.py read-all         # 读取所有表结构
    python db_schema.py search <关键字>  # 搜索表或字段
    python db_schema.py relations        # 分析表关联关系
    python db_schema.py validate <文件>  # 验证SQL文件
    python db_schema.py update [表名...]  # 增量更新表结构
"""

import sys
import os
import json
from datetime import datetime

def load_config():
    """加载配置文件"""
    config_file = '.claude/db-schema/config.json'
    if not os.path.exists(config_file):
        return None
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置文件"""
    os.makedirs('.claude/db-schema', exist_ok=True)
    with open('.claude/db-schema/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def print_help():
    """显示帮助信息"""
    help_text = """
db-schema - 数据库表结构管理工具 v1.0.0

命令:
    init              初始化配置（收集数据库连接信息）
    read-all          读取所有表结构
    search <关键字>    搜索表名或字段
    relations         分析表关联关系
    validate <文件>   验证SQL文件（检测字段是否存在、NOT NULL误用）
    update [表名...]  增量更新表结构（不指定表名则更新所有变化的表）

示例:
    python db_schema.py init
    python db_schema.py read-all
    python db_schema.py search user_id
    python db_schema.py relations
    python db_schema.py validate mapper/OrderMapper.xml
    python db_schema.py update
    python db_schema.py update t_user t_order

文档位置:
    .claude/db-schema/
    ├── tables/           # 表结构文档
    ├── relations.md      # 表关联关系
    ├── summary.md        # 汇总索引
    └── config.json       # 配置信息

安全提示:
    config.json 包含数据库连接信息，请确保已添加到 .gitignore
"""
    print(help_text)

def cmd_init():
    """初始化配置"""
    print("=" * 50)
    print("数据库连接配置")
    print("=" * 50)
    print("\n请提供数据库连接信息：")
    print("注意：prod 环境禁止连接\n")

    host = input("主机地址: ").strip()
    if not host:
        print("错误: 主机地址不能为空")
        return

    port_str = input("端口 (默认3306): ").strip()
    port = int(port_str) if port_str else 3306

    user = input("用户名: ").strip()
    if not user:
        print("错误: 用户名不能为空")
        return

    password = input("密码: ").strip()
    if not password:
        print("错误: 密码不能为空")
        return

    database = input("数据库名: ").strip()
    if not database:
        print("错误: 数据库名不能为空")
        return

    environment = input("环境 (local/dev/test/uat): ").strip().lower()
    if environment not in ['local', 'dev', 'test', 'uat']:
        print("错误: 环境只能是 local/dev/test/uat，prod 禁止连接")
        return

    config = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "environment": environment,
        "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "last_update": None,
        "table_count": 0,
        "compression": True
    }

    save_config(config)
    print(f"\n配置已保存到 .claude/db-schema/config.json")
    print("\n提示: 请确保将该文件添加到 .gitignore")

def cmd_read_all():
    """读取所有表结构"""
    config = load_config()
    if not config:
        print("错误: 未找到配置文件，请先运行 'python db_schema.py init'")
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
        SELECT TABLE_NAME, TABLE_COMMENT, TABLE_ROWS
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
    """)
    tables = cursor.fetchall()

    print(f"\n找到 {len(tables)} 个表，开始读取...")

    os.makedirs('.claude/db-schema/tables', exist_ok=True)

    summary_data = []
    success_count = 0

    for i, (table_name, table_comment, table_rows) in enumerate(tables):
        try:
            # 获取字段信息
            cursor.execute("""
                SELECT
                    COLUMN_NAME,
                    COLUMN_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (table_name,))
            columns = cursor.fetchall()

            # 生成文档
            doc = f"# {table_name}"
            if table_comment:
                doc += f" — {table_comment}"
            doc += "\n\n"

            doc += "## 基本信息\n"
            doc += f"- **表名**: {table_name}\n"
            if table_comment:
                doc += f"- **说明**: {table_comment}\n"
            doc += f"- **预估行数**: ~{table_rows}\n\n"

            doc += "## 字段清单\n\n"
            doc += "| 字段 | 类型 | 可空 | 默认值 | 说明 |\n"
            doc += "|------|------|------|--------|------|\n"

            for col in columns:
                field, col_type, nullable, default, col_comment = col
                nullable_str = 'N' if nullable == 'NO' else 'Y'
                default_str = str(default) if default else '-'
                comment_str = col_comment if col_comment else '-'
                doc += f"| {field} | {col_type} | {nullable_str} | {default_str} | {comment_str} |\n"

            # 保存文档
            table_file = f".claude/db-schema/tables/{table_name}.md"
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(doc)

            summary_data.append({
                'name': table_name,
                'comment': table_comment or '',
                'rows': table_rows or 0,
                'columns': len(columns)
            })

            success_count += 1
            if (i + 1) % 50 == 0:
                print(f"  已处理 {i + 1}/{len(tables)} 个表...")

        except Exception as e:
            print(f"  [错误] {table_name}: {e}")

    # 保存汇总数据
    with open('.claude/db-schema/summary_data.json', 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

    # 生成汇总文档
    summary_doc = "# 数据库表结构汇总\n\n"
    summary_doc += f"- 总表数: {len(summary_data)}\n"
    summary_doc += f"- 数据库: {config['database']}\n"
    summary_doc += f"- 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    summary_doc += "| 表名 | 说明 | 字段数 | 预估行数 |\n"
    summary_doc += "|------|------|--------|----------|\n"
    for t in summary_data:
        summary_doc += f"| {t['name']} | {t['comment']} | {t['columns']} | ~{t['rows']} |\n"

    with open('.claude/db-schema/summary.md', 'w', encoding='utf-8') as f:
        f.write(summary_doc)

    # 更新配置
    config['last_update'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    config['table_count'] = len(tables)
    save_config(config)

    cursor.close()
    conn.close()

    print(f"\n完成! 成功读取 {success_count}/{len(tables)} 个表")
    print(f"文档保存在 .claude/db-schema/")

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    if command == 'init':
        cmd_init()

    elif command == 'read-all':
        cmd_read_all()

    elif command == 'search':
        if not args:
            print("用法: python db_schema.py search <关键字>")
            return
        # 添加脚本目录到路径
        script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        if os.path.exists(script_dir):
            sys.path.insert(0, script_dir)
        from search_schema import search_schema
        search_schema(args[0])

    elif command == 'relations':
        script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        if os.path.exists(script_dir):
            sys.path.insert(0, script_dir)
        from analyze_relations import analyze_relations
        analyze_relations()

    elif command == 'validate':
        if not args:
            print("用法: python db_schema.py validate <SQL文件>")
            return
        script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        if os.path.exists(script_dir):
            sys.path.insert(0, script_dir)
        from validate_sql import validate_sql
        validate_sql(args[0])

    elif command == 'update':
        script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        if os.path.exists(script_dir):
            sys.path.insert(0, script_dir)
        from update_schema import update_tables
        update_tables(args if args else None)

    else:
        print(f"未知命令: {command}")
        print_help()

if __name__ == '__main__':
    main()
---
name: db-schema
preamble-tier: 2
version: 1.0.0
description: |
  数据库表结构读取和管理工具。读取数据库表结构、字段信息、表关联关系，
  生成压缩文档供SQL编写时参考。支持手动更新和增量同步。
  解决问题：字段不存在、NOT NULL字段误用is not null、表关联不清晰。
  Use when asked to "表结构", "db-schema", "读取数据库", "表关联"。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
triggers:
  - db-schema
  - 表结构
  - 读取数据库
  - 表关联
  - 数据库结构
---

# /db-schema — 数据库表结构管理 v1.0.0

你是一位**数据库架构师**，负责读取和管理数据库表结构，生成便于SQL编写的参考文档。

## 首次使用

### 步骤1：配置数据库连接

用户需要提供数据库连接信息，使用 AskUserQuestion 收集：

```
请提供数据库连接信息：
- 主机地址 (host)
- 端口 (port，默认3306)
- 用户名 (username)
- 密码 (password)
- 数据库名 (database)
- 环境 (environment: local/dev/test/uat，prod禁止)
```

### 步骤2：生成配置文件

将连接信息保存到项目目录（不提交到git）：

```
.claude/db-schema/config.json
```

**重要安全规则：**
- 连接信息只保存在项目的 `.claude/db-schema/` 目录
- 该目录应添加到 `.gitignore`
- 禁止连接 prod 环境
- 禁止在代码或文档中硬编码连接信息

---

## 核心功能

| 功能 | 说明 |
|------|------|
| 读取表结构 | 从数据库读取表结构、字段信息、索引 |
| 分析关联关系 | 识别外键关联、业务关联 |
| 生成压缩文档 | 输出简洁的表结构文档 |
| 字段搜索 | 搜索包含某字段的所有表 |
| SQL验证 | 验证字段是否存在、NOT NULL误用检测 |
| 增量更新 | 检测表结构变化并更新 |

---

## 命令模式

- `/db-schema` — 显示帮助和当前状态
- `/db-schema init` — 初始化配置（收集数据库连接信息）
- `/db-schema read-all` — 读取所有表结构
- `/db-schema read <表名>` — 读取指定表结构
- `/db-schema search <关键字>` — 搜索表或字段
- `/db-schema relations` — 分析表关联关系
- `/db-schema validate <SQL文件>` — 验证SQL字段是否存在
- `/db-schema update [表名...]` — 增量更新表结构

---

## 文档存储位置

```
.claude/db-schema/
├── config.json          # 配置信息（含连接信息，不提交git）
├── tables/              # 表结构文档
│   ├── t_user.md
│   ├── t_order.md
│   └── ...
├── relations.md         # 表关联关系
├── relations_data.json  # 关联关系结构化数据
├── summary.md           # 汇总索引
├── summary_data.json    # 结构化数据
├── db_schema.py         # 统一入口脚本
├── search_schema.py     # 字段搜索脚本
├── analyze_relations.py # 关联分析脚本
├── validate_sql.py      # SQL验证脚本
└── update_schema.py     # 增量更新脚本
```

---

## 数据库连接方法

当前环境没有 MySQL CLI，使用 Python + PyMySQL 连接：

```python
import pymysql

# 从 config.json 读取连接信息
conn = pymysql.connect(
    host='<从配置读取>',
    port=3306,
    user='<从配置读取>',
    password='<从配置读取>',
    database='<从配置读取>',
    charset='utf8mb4'
)
```

---

## 初始化流程

### 1. 收集连接信息

```python
# 使用 AskUserQuestion 收集信息
questions = [
    {"question": "数据库主机地址?", "header": "Host"},
    {"question": "数据库端口?", "header": "Port", "default": "3306"},
    {"question": "用户名?", "header": "Username"},
    {"question": "密码?", "header": "Password"},
    {"question": "数据库名?", "header": "Database"},
    {"question": "环境 (local/dev/test/uat)?", "header": "Environment"}
]
```

### 2. 生成配置文件

```python
import json
from datetime import datetime

config = {
    "host": "<用户输入>",
    "port": 3306,
    "user": "<用户输入>",
    "password": "<用户输入>",
    "database": "<用户输入>",
    "environment": "<用户输入>",
    "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "last_update": None,
    "table_count": 0,
    "compression": True
}

# 保存到项目目录（不提交git）
with open('.claude/db-schema/config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
```

### 3. 创建 .gitignore 规则

确保 `.claude/db-schema/config.json` 不被提交：

```gitignore
# 数据库配置（含敏感信息）
.claude/db-schema/config.json
```

---

## 脚本模板

### db_schema.py（统一入口）

```python
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

def load_config():
    """加载配置文件"""
    config_file = '.claude/db-schema/config.json'
    if not os.path.exists(config_file):
        print("错误: 未找到配置文件，请先运行 'python db_schema.py init'")
        return None
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_help():
    """显示帮助信息"""
    help_text = """
db-schema - 数据库表结构管理工具 v1.0.0

命令:
    init              初始化配置（收集数据库连接信息）
    read-all          读取所有表结构
    search <关键字>    搜索表名或字段
    relations         分析表关联关系
    validate <文件>   验证SQL文件
    update [表名...]  增量更新表结构

示例:
    python db_schema.py init
    python db_schema.py read-all
    python db_schema.py search user_id
    python db_schema.py relations
    python db_schema.py validate mapper/OrderMapper.xml
    python db_schema.py update
"""
    print(help_text)

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    if command == 'init':
        # 初始化配置
        print("请提供数据库连接信息：")
        host = input("主机地址: ")
        port = input("端口 (默认3306): ") or "3306"
        user = input("用户名: ")
        password = input("密码: ")
        database = input("数据库名: ")
        environment = input("环境 (local/dev/test/uat): ")

        config = {
            "host": host,
            "port": int(port),
            "user": user,
            "password": password,
            "database": database,
            "environment": environment,
            "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "table_count": 0
        }

        os.makedirs('.claude/db-schema', exist_ok=True)
        with open('.claude/db-schema/config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("配置已保存到 .claude/db-schema/config.json")

    elif command == 'search':
        if not args:
            print("用法: python db_schema.py search <关键字>")
            return
        from search_schema import search_schema
        search_schema(args[0])

    elif command == 'relations':
        from analyze_relations import analyze_relations
        analyze_relations()

    elif command == 'validate':
        if not args:
            print("用法: python db_schema.py validate <SQL文件>")
            return
        from validate_sql import validate_sql
        validate_sql(args[0])

    elif command == 'update':
        from update_schema import update_tables
        update_tables(args if args else None)

    else:
        print(f"未知命令: {command}")
        print_help()

if __name__ == '__main__':
    main()
```

---

## 重要规则

1. **禁止连接prod环境**
2. **连接信息只保存在 config.json，不提交git**
3. **文档使用压缩格式**
4. **手动标注放在特定标记内**
5. **增量更新保留手动标注**
6. **SQL验证提供修复建议**

---

## 安全建议

### .gitignore 配置

```gitignore
# 数据库配置文件（含敏感信息）
.claude/db-schema/config.json
```

### 环境变量方式（可选）

也可以通过环境变量传递连接信息：

```bash
export DB_HOST=your_host
export DB_PORT=3306
export DB_USER=your_user
export DB_PASSWORD=your_password
export DB_NAME=your_database
```

---

## 与 dev-flow 集成

在 `/dev-flow` 的以下阶段可调用此skill：

1. **代码分析阶段**：读取相关表结构
2. **开发计划阶段**：验证数据库变更
3. **SQL编写时**：提供字段提示

调用方式：
```
使用 Skill 工具调用 db-schema
参数：search <关键字> 或 validate <SQL文件>
```
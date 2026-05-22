# db-schema - 数据库表结构管理工具

一个用于读取和管理数据库表结构的工具，生成便于SQL编写的参考文档。

## 功能特性

| 功能 | 说明 |
|------|------|
| 读取表结构 | 从数据库读取表结构、字段信息、索引 |
| 分析关联关系 | 识别外键关联、业务关联 |
| 生成压缩文档 | 输出简洁的表结构文档 |
| 字段搜索 | 搜索包含某字段的所有表 |
| SQL验证 | 验证字段是否存在、NOT NULL误用检测 |
| 增量更新 | 检测表结构变化并更新 |

## 安装

### 1. 安装依赖

```bash
pip install pymysql
```

### 2. 安装 Skill

将 `skill.md` 复制到你的 Claude Code skills 目录：

```bash
# Windows
copy skill.md %USERPROFILE%\.claude\skills\db-schema\skill.md

# macOS/Linux
cp skill.md ~/.claude/skills/db-schema/skill.md
```

将 `scripts/` 目录复制到你的项目根目录：

```bash
# 复制到项目的 .claude/db-schema/ 目录
cp -r scripts/* your-project/.claude/db-schema/
```

## 使用方法

### 命令行

```bash
# 初始化配置（收集数据库连接信息）
python .claude/db-schema/scripts/db_schema.py init

# 读取所有表结构
python .claude/db-schema/scripts/db_schema.py read-all

# 搜索字段
python .claude/db-schema/scripts/db_schema.py search user_id

# 分析表关联关系
python .claude/db-schema/scripts/db_schema.py relations

# 验证SQL文件
python .claude/db-schema/scripts/db_schema.py validate mapper.xml

# 增量更新表结构
python .claude/db-schema/scripts/db_schema.py update
```

### Claude Code Skill

在 Claude Code 中使用：

```
/db-schema search user_id
/db-schema relations
/db-schema validate path/to/mapper.xml
```

## 安全说明

**重要：数据库连接信息安全**

1. 连接信息保存在 `.claude/db-schema/config.json`
2. 该文件**必须**添加到 `.gitignore`：

```gitignore
# 数据库配置（含敏感信息）
.claude/db-schema/config.json
```

3. **禁止连接 prod 环境**，只允许 local/dev/test/uat

## 文档结构

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
└── scripts/             # 脚本文件
    ├── db_schema.py     # 统一入口
    ├── search_schema.py
    ├── analyze_relations.py
    ├── validate_sql.py
    └── update_schema.py
```

## 解决的问题

1. **字段不存在**: 验证SQL字段是否在表结构中
2. **NOT NULL误用**: 检测 `WHERE xx IS NOT NULL` 但字段定义为 NOT NULL
3. **表关联不清晰**: 分析并记录表关联关系

## 许可证

MIT License
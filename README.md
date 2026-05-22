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

## 快速安装

### 一行命令安装（推荐）

**Linux / macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main/install | bash
```

**Windows (PowerShell):**
```powershell
pip install pymysql && python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main/install.py').read())"
```

**通用方式:**
```bash
pip install pymysql
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main/install.py').read())"
```

### 手动安装

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

## 核心价值

db-schema 致力于解决 SQL 开发过程中的三大痛点：

### 1. 字段引用错误预防

**问题场景**：开发人员编写 SQL 时引用了不存在或已废弃的字段，导致运行时报错或查询结果异常。

**解决方案**：通过静态分析验证 SQL 语句中的字段引用，在编码阶段即可发现潜在错误，避免问题流入生产环境。

**典型案例**：
- `SELECT non_exist_field FROM t_user` → 提示字段不存在
- `WHERE status = 1` 但 status 字段已从表中移除 → 提前预警

### 2. 冗余条件检测优化

**问题场景**：NOT NULL 字段在 WHERE 条件中使用 `IS NOT NULL` 判断，产生无意义的冗余逻辑，影响 SQL 可读性和执行效率。

**解决方案**：智能识别字段约束定义，自动检测冗余的 NULL 判断条件，提供优化建议。

**典型案例**：
- `WHERE create_time IS NOT NULL` 但 create_time 定义为 `NOT NULL`
- 冗余判断导致 SQL 逻辑复杂化，增加维护成本

### 3. 表关联关系可视化

**问题场景**：复杂业务系统中表数量众多，外键约束缺失或命名不规范，开发人员难以快速理解表之间的关联关系，导致 JOIN 语句编写困难。

**解决方案**：基于命名约定（xxx_id）智能推断表关联关系，生成结构化的关联文档，辅助开发人员快速定位关联路径。

**典型案例**：
- `t_order.user_id` → 推断关联 `t_user.id`
- `t_order_item.order_id` → 推断关联 `t_order.id`
- 一键生成完整的表关联图谱

---

## 适用场景

| 场景 | 价值 |
|------|------|
| 新项目开发 | 快速了解数据库结构，降低上手成本 |
| SQL 编写 | 实时验证字段引用，减少运行时错误 |
| 代码审查 | 自动检测 SQL 问题，提升代码质量 |
| 数据库迁移 | 增量同步表结构变化，保持文档最新 |
| 团队协作 | 共享表结构文档，统一认知基准 |

## 许可证

MIT License
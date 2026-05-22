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

---

## 一键安装

### Windows (推荐)

打开 PowerShell，在项目目录下执行：

```powershell
pip install pymysql && python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main/install.py').read())"
```

### Linux / macOS

```bash
pip install pymysql && python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main/install.py').read())"
```

### 安装过程

安装脚本会自动完成以下步骤：

1. ✅ 安装 PyMySQL 依赖
2. ✅ 下载 skill.md 到 `~/.claude/skills/db-schema/`
3. ✅ 下载脚本到项目的 `.claude/db-schema/scripts/`
4. ✅ 交互式配置数据库连接
5. ✅ 自动添加 `.gitignore` 规则
6. ✅ 可选：立即读取所有表结构

安装完成后，在 Claude Code 中使用 `/db-schema` 命令即可。

---

## 使用方法

### Claude Code 中使用

```
/db-schema              显示帮助
/db-schema search xxx   搜索字段
/db-schema relations    分析表关联
/db-schema validate xxx 验证SQL
/db-schema update       更新表结构
```

### 命令行使用

```bash
# 搜索字段
python .claude/db-schema/scripts/db_schema.py search user_id

# 分析表关联关系
python .claude/db-schema/scripts/db_schema.py relations

# 验证SQL文件
python .claude/db-schema/scripts/db_schema.py validate mapper.xml

# 增量更新表结构
python .claude/db-schema/scripts/db_schema.py update
```

---

## 安全说明

**重要：数据库连接信息安全**

1. 连接信息保存在 `.claude/db-schema/config.json`
2. 安装脚本会自动添加到 `.gitignore`
3. **禁止连接 prod 环境**，只允许 local/dev/test/uat

---

## 文档结构

```
.claude/db-schema/
├── config.json          # 配置信息（含连接信息，不提交git）
├── tables/              # 表结构文档
├── relations.md         # 表关联关系
├── summary.md           # 汇总索引
└── scripts/             # 脚本文件
```

---

## 核心价值

### 1. 字段引用错误预防

开发人员编写 SQL 时引用了不存在或已废弃的字段，导致运行时报错。通过静态分析验证 SQL 语句中的字段引用，在编码阶段即可发现潜在错误。

### 2. 冗余条件检测优化

NOT NULL 字段在 WHERE 条件中使用 `IS NOT NULL` 判断，产生无意义的冗余逻辑。智能识别字段约束定义，自动检测冗余的 NULL 判断条件。

### 3. 表关联关系可视化

复杂业务系统中表数量众多，开发人员难以快速理解表之间的关联关系。基于命名约定（xxx_id）智能推断表关联关系，生成结构化的关联文档。

---

## 许可证

MIT License
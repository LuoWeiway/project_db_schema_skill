# db-schema Skill 安装指南

## 快速安装

### 方式一：自动安装（推荐）

```bash
# 1. 克隆或下载本项目
git clone <repository-url> db-schema-skill
cd db-schema-skill

# 2. 运行安装脚本
python install.py

# 3. 在项目中初始化
cd your-project
mkdir -p .claude/db-schema/scripts
cp -r /path/to/db-schema-skill/scripts/* .claude/db-schema/scripts/

# 4. 安装依赖
pip install pymysql

# 5. 初始化配置
python .claude/db-schema/scripts/db_schema.py init
```

### 方式二：手动安装

#### 步骤 1：安装 Skill 到 Claude Code

**Windows:**
```powershell
# 创建目录
mkdir %USERPROFILE%\.claude\skills\db-schema

# 复制 skill.md
copy skill.md %USERPROFILE%\.claude\skills\db-schema\skill.md
```

**macOS/Linux:**
```bash
# 创建目录
mkdir -p ~/.claude/skills/db-schema

# 复制 skill.md
cp skill.md ~/.claude/skills/db-schema/skill.md
```

#### 步骤 2：在项目中安装脚本

```bash
# 进入你的项目目录
cd your-project

# 创建目录结构
mkdir -p .claude/db-schema/scripts

# 复制脚本文件
cp -r /path/to/db-schema-skill/scripts/* .claude/db-schema/scripts/
```

#### 步骤 3：安装 Python 依赖

```bash
pip install pymysql
```

#### 步骤 4：初始化数据库配置

```bash
python .claude/db-schema/scripts/db_schema.py init
```

按提示输入数据库连接信息：
- 主机地址
- 端口（默认 3306）
- 用户名
- 密码
- 数据库名
- 环境（local/dev/test/uat）

#### 步骤 5：读取表结构

```bash
python .claude/db-schema/scripts/db_schema.py read-all
```

#### 步骤 6：配置 .gitignore

确保敏感信息不被提交：

```bash
# 添加到 .gitignore
echo ".claude/db-schema/config.json" >> .gitignore
```

---

## 使用方法

### 命令行

```bash
# 搜索字段
python .claude/db-schema/scripts/db_schema.py search user_id

# 分析表关联关系
python .claude/db-schema/scripts/db_schema.py relations

# 验证 SQL 文件
python .claude/db-schema/scripts/db_schema.py validate mapper.xml

# 增量更新表结构
python .claude/db-schema/scripts/db_schema.py update
```

### Claude Code 中使用

```
/db-schema search user_id
/db-schema relations
/db-schema validate path/to/mapper.xml
```

---

## 目录结构

安装完成后的目录结构：

```
~/.claude/skills/db-schema/
└── skill.md              # Skill 定义文件

your-project/
└── .claude/db-schema/
    ├── config.json       # 数据库配置（不提交 git）
    ├── tables/           # 表结构文档
    ├── relations.md      # 表关联关系
    ├── summary.md        # 汇总索引
    └── scripts/          # 脚本文件
        ├── db_schema.py
        ├── search_schema.py
        ├── analyze_relations.py
        ├── validate_sql.py
        └── update_schema.py
```

---

## 安全说明

1. **config.json 包含数据库密码**，必须添加到 `.gitignore`
2. **禁止连接 prod 环境**
3. 只允许连接 local/dev/test/uat 环境

---

## 常见问题

### Q: 提示 "未找到配置文件"

A: 先运行 `python db_schema.py init` 初始化配置

### Q: 提示 "需要安装 PyMySQL"

A: 运行 `pip install pymysql`

### Q: 如何在多个项目中使用？

A: Skill 只需安装一次（到 `~/.claude/skills/`），但每个项目需要：
1. 复制 scripts 目录到项目的 `.claude/db-schema/scripts/`
2. 运行 `python db_schema.py init` 配置该项目的数据库

### Q: 如何更新 Skill？

A: 重新复制 `skill.md` 到 `~/.claude/skills/db-schema/`，并更新项目的 scripts 目录

---

## 卸载

```bash
# Windows
rmdir /s %USERPROFILE%\.claude\skills\db-schema

# macOS/Linux
rm -rf ~/.claude/skills/db-schema

# 删除项目中的文件
rm -rf your-project/.claude/db-schema
```
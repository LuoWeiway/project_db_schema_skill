# db-schema Skill 安装指南

## 一键安装（推荐）

### Windows

在项目目录下打开 PowerShell，执行：

```powershell
pip install pymysql && python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main/install.py').read())"
```

### Linux / macOS

```bash
pip install pymysql && python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main/install.py').read())"
```

---

## 安装过程

脚本会自动完成：

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | 安装 PyMySQL | ✅ 依赖就绪 |
| 2 | 下载 skill.md | ✅ Claude Code 可识别 |
| 3 | 下载脚本 | ✅ 项目目录就绪 |
| 4 | 配置数据库 | ✅ 交互式输入 |
| 5 | 更新 .gitignore | ✅ 敏感信息保护 |
| 6 | 读取表结构 | ✅ 可选，立即使用 |

---

## 安装后验证

```bash
# 测试命令行
python .claude/db-schema/scripts/db_schema.py search user

# 在 Claude Code 中测试
/db-schema
```

---

## 手动安装（离线环境）

如果无法访问网络，可以手动安装：

### 1. 安装依赖

```bash
pip install pymysql
```

### 2. 复制文件

```
skill.md → ~/.claude/skills/db-schema/skill.md
scripts/* → your-project/.claude/db-schema/scripts/
```

### 3. 初始化配置

```bash
python .claude/db-schema/scripts/db_schema.py init
```

### 4. 读取表结构

```bash
python .claude/db-schema/scripts/db_schema.py read-all
```

### 5. 配置 .gitignore

```bash
echo ".claude/db-schema/config.json" >> .gitignore
```

---

## 常见问题

### Q: 提示 "未找到配置文件"

A: 先运行 `python .claude/db-schema/scripts/db_schema.py init`

### Q: 提示 "需要安装 PyMySQL"

A: 运行 `pip install pymysql`

### Q: 如何在多个项目中使用？

A: Skill 只需安装一次，每个项目需要：
1. 在项目目录运行安装命令
2. 或手动复制 scripts 目录

### Q: 如何更新？

A: 重新运行一键安装命令即可

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
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
db-schema skill 一键安装脚本 v2.0
真正的"一键安装" - 自动完成所有步骤

使用方法:
  pip install pymysql && python install.py

或者从网络安装:
  pip install pymysql && python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main/install.py').read())"
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

REPO_URL = "https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main"

def get_claude_skills_dir():
    """获取 Claude skills 目录"""
    if sys.platform == 'win32':
        base = os.environ.get('USERPROFILE', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~')
    return Path(base) / '.claude' / 'skills' / 'db-schema'

def get_project_db_schema_dir():
    """获取项目中的 db-schema 目录"""
    return Path.cwd() / '.claude' / 'db-schema'

def download_file(url, dest):
    """下载文件"""
    try:
        import urllib.request
        print(f"  下载: {url}")
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        return False

def install_pymysql():
    """安装 PyMySQL"""
    print("\n[步骤 1/4] 安装 PyMySQL...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pymysql', '-q'],
                      check=True, capture_output=True)
        print("  ✅ PyMySQL 已安装")
        return True
    except subprocess.CalledProcessError:
        print("  ⚠️ PyMySQL 安装失败，请手动运行: pip install pymysql")
        return False

def install_skill():
    """安装 skill.md 到 Claude skills 目录"""
    print("\n[步骤 2/4] 安装 skill 到 Claude Code...")

    skills_dir = get_claude_skills_dir()
    skills_dir.mkdir(parents=True, exist_ok=True)

    skill_file = skills_dir / 'skill.md'
    skill_url = f"{REPO_URL}/skill.md"

    if download_file(skill_url, skill_file):
        print(f"  ✅ skill.md 已安装到: {skills_dir}")
        return True
    return False

def install_scripts():
    """安装脚本到项目目录"""
    print("\n[步骤 3/4] 安装脚本到项目...")

    project_dir = get_project_db_schema_dir()
    scripts_dir = project_dir / 'scripts'
    scripts_dir.mkdir(parents=True, exist_ok=True)

    scripts = ['db_schema.py', 'search_schema.py', 'analyze_relations.py',
               'validate_sql.py', 'update_schema.py']

    success_count = 0
    for script in scripts:
        script_url = f"{REPO_URL}/scripts/{script}"
        script_file = scripts_dir / script
        if download_file(script_url, script_file):
            success_count += 1

    if success_count == len(scripts):
        print(f"  ✅ {success_count} 个脚本已安装到: {scripts_dir}")
        return True
    else:
        print(f"  ⚠️ 只安装了 {success_count}/{len(scripts)} 个脚本")
        return False

def init_config_interactive():
    """交互式初始化配置"""
    print("\n[步骤 4/4] 配置数据库连接...")
    print("\n请提供数据库连接信息（仅支持 local/dev/test/uat，禁止 prod）：")

    host = input("  主机地址: ").strip()
    if not host:
        print("  ❌ 主机地址不能为空")
        return False

    port = input("  端口 (默认3306): ").strip() or "3306"
    user = input("  用户名: ").strip()
    if not user:
        print("  ❌ 用户名不能为空")
        return False

    password = input("  密码: ").strip()
    database = input("  数据库名: ").strip()
    if not database:
        print("  ❌ 数据库名不能为空")
        return False

    environment = input("  环境 (local/dev/test/uat): ").strip().lower()
    if environment not in ['local', 'dev', 'test', 'uat']:
        print("  ❌ 环境必须是 local/dev/test/uat，禁止 prod")
        return False

    config = {
        "host": host,
        "port": int(port),
        "user": user,
        "password": password,
        "database": database,
        "environment": environment,
        "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "last_update": None,
        "table_count": 0
    }

    config_file = get_project_db_schema_dir() / 'config.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"  ✅ 配置已保存到: {config_file}")

    # 添加到 .gitignore
    gitignore = Path.cwd() / '.gitignore'
    gitignore_entry = ".claude/db-schema/config.json"

    if gitignore.exists():
        with open(gitignore, 'r', encoding='utf-8') as f:
            content = f.read()
        if gitignore_entry not in content:
            with open(gitignore, 'a', encoding='utf-8') as f:
                f.write(f"\n# db-schema 数据库配置（含敏感信息）\n{gitignore_entry}\n")
            print("  ✅ 已添加到 .gitignore")
    else:
        with open(gitignore, 'w', encoding='utf-8') as f:
            f.write(f"# db-schema 数据库配置（含敏感信息）\n{gitignore_entry}\n")
        print("  ✅ 已创建 .gitignore")

    return True

def read_all_tables():
    """读取所有表结构"""
    print("\n[可选] 是否立即读取所有表结构？(y/n): ")
    choice = input().strip().lower()

    if choice == 'y':
        scripts_dir = get_project_db_schema_dir() / 'scripts'
        db_schema_py = scripts_dir / 'db_schema.py'

        print("  正在读取表结构...")
        result = subprocess.run([sys.executable, str(db_schema_py), 'read-all'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("  ✅ 表结构已读取")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        else:
            print(f"  ❌ 读取失败: {result.stderr}")
    else:
        print("  略过，稍后可运行: python .claude/db-schema/scripts/db_schema.py read-all")

def main():
    print("\n" + "=" * 60)
    print("     db-schema Skill 一键安装程序 v2.0")
    print("     Database Schema Management Tool")
    print("=" * 60)
    print(f"\n  安装目录: {get_claude_skills_dir()}")
    print(f"  项目目录: {get_project_db_schema_dir()}")

    # 步骤 1: 安装 PyMySQL
    if not install_pymysql():
        print("\n❌ 安装失败，请先运行: pip install pymysql")
        return

    # 步骤 2: 安装 skill
    if not install_skill():
        print("\n❌ skill 安装失败")
        return

    # 步骤 3: 安装脚本
    if not install_scripts():
        print("\n❌ 脚本安装失败")
        return

    # 步骤 4: 配置数据库
    if not init_config_interactive():
        print("\n❌ 配置失败")
        return

    # 可选: 读取表结构
    read_all_tables()

    # 完成
    print("\n" + "=" * 60)
    print("           ✅ 安装成功！")
    print("=" * 60)
    print("\n现在可以在 Claude Code 中使用以下命令：")
    print("  /db-schema              显示帮助")
    print("  /db-schema search xxx   搜索字段")
    print("  /db-schema relations    分析表关联")
    print("  /db-schema validate xxx 验证SQL")
    print("  /db-schema update       更新表结构")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
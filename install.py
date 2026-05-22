#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
db-schema skill 一键安装脚本 (Windows/通用版本)
使用方法:
  pip install pymysql && python install.py
"""

import os
import sys
import subprocess
from pathlib import Path

def get_skills_dir():
    """获取 Claude skills 目录"""
    if sys.platform == 'win32':
        base = os.environ.get('USERPROFILE', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~')
    return Path(base) / '.claude' / 'skills' / 'db-schema'

def download_file(url, dest):
    """下载文件"""
    try:
        import urllib.request
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False

def main():
    print("\n" + "=" * 50)
    print("     db-schema Skill 安装程序 v1.0.0")
    print("     Database Schema Management Tool")
    print("=" * 50 + "\n")

    # 检查 Python
    print("[INFO] Python 版本:", sys.version.split()[0])

    # 安装 PyMySQL
    print("[INFO] 安装 PyMySQL...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pymysql', '-q'],
                      check=True, capture_output=True)
        print("[SUCCESS] PyMySQL 已安装")
    except subprocess.CalledProcessError:
        print("[WARN] PyMySQL 安装失败，请手动运行: pip install pymysql")

    # 创建目录
    skills_dir = get_skills_dir()
    print(f"[INFO] 安装目录: {skills_dir}")
    skills_dir.mkdir(parents=True, exist_ok=True)

    # 下载 skill.md
    repo_url = "https://raw.githubusercontent.com/LuoWeiway/project_db_schema_skill/main"
    skill_url = f"{repo_url}/skill.md"
    skill_file = skills_dir / 'skill.md'

    print("[INFO] 下载 skill.md...")
    if download_file(skill_url, skill_file):
        print("[SUCCESS] skill.md 已安装")
    else:
        print("[ERROR] 下载失败，请手动下载")
        return

    # 显示后续步骤
    print("\n" + "=" * 50)
    print("           安装成功！")
    print("=" * 50 + "\n")

    print("后续步骤:\n")
    print("1. 在项目中创建目录:")
    print("   mkdir .claude\\db-schema\\scripts  (Windows)")
    print("   mkdir -p .claude/db-schema/scripts  (Linux/Mac)\n")

    print("2. 下载脚本文件到项目:")
    scripts = ['db_schema.py', 'search_schema.py', 'analyze_relations.py',
               'validate_sql.py', 'update_schema.py']
    for script in scripts:
        print(f"   {repo_url}/scripts/{script}")

    print("\n3. 初始化数据库配置:")
    print("   python .claude/db-schema/scripts/db_schema.py init\n")

    print("4. 读取表结构:")
    print("   python .claude/db-schema/scripts/db_schema.py read-all\n")

    print("5. 添加到 .gitignore:")
    print("   .claude/db-schema/config.json\n")

    print("=" * 50)
    print("现在可以在 Claude Code 中使用 /db-schema 命令了！")
    print("=" * 50 + "\n")

if __name__ == '__main__':
    main()
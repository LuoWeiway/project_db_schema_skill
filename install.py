#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
db-schema skill 安装脚本
将 skill 安装到 Claude Code
"""

import os
import sys
import shutil
from pathlib import Path

def get_claude_skills_dir():
    """获取 Claude Code skills 目录"""
    if sys.platform == 'win32':
        # Windows
        base = os.environ.get('USERPROFILE', os.path.expanduser('~'))
    else:
        # macOS/Linux
        base = os.path.expanduser('~')

    return Path(base) / '.claude' / 'skills' / 'db-schema'

def install():
    """安装 skill"""
    # 获取当前目录
    current_dir = Path(__file__).parent

    # 目标目录
    skills_dir = get_claude_skills_dir()
    skills_dir.mkdir(parents=True, exist_ok=True)

    # 复制 skill.md
    skill_src = current_dir / 'skill.md'
    skill_dst = skills_dir / 'skill.md'

    if skill_dst.exists():
        print(f"警告: {skill_dst} 已存在")
        response = input("是否覆盖? (y/n): ").strip().lower()
        if response != 'y':
            print("安装取消")
            return

    shutil.copy2(skill_src, skill_dst)
    print(f"\n✓ skill.md 已安装到: {skill_dst}")

    # 显示后续步骤
    print("\n" + "=" * 50)
    print("安装完成!")
    print("=" * 50)
    print("\n后续步骤:")
    print("\n1. 在项目中创建 .claude/db-schema/ 目录:")
    print("   mkdir -p .claude/db-schema/scripts")
    print("\n2. 复制脚本文件到项目:")
    print(f"   cp -r {current_dir}/scripts/* .claude/db-schema/scripts/")
    print("\n3. 安装 Python 依赖:")
    print("   pip install pymysql")
    print("\n4. 初始化数据库配置:")
    print("   python .claude/db-schema/scripts/db_schema.py init")
    print("\n5. 读取表结构:")
    print("   python .claude/db-schema/scripts/db_schema.py read-all")
    print("\n6. 添加到 .gitignore:")
    print("   .claude/db-schema/config.json")
    print("\n现在可以在 Claude Code 中使用 /db-schema 命令了!")

if __name__ == '__main__':
    install()
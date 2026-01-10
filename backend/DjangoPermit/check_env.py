#!/usr/bin/env python
"""
检查当前使用的 Python 环境
"""
import sys
import os

print("=" * 60)
print("Python 环境信息")
print("=" * 60)
print(f"Python 可执行文件路径: {sys.executable}")
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.path[0]}")
print()

# 检查是否在虚拟环境中
venv_path = os.path.dirname(os.path.dirname(sys.executable))
if 'venv' in sys.executable.lower() or '.venv' in sys.executable.lower():
    print("✓ 正在使用虚拟环境")
    print(f"虚拟环境路径: {venv_path}")
else:
    print("✗ 未使用虚拟环境（使用的是系统 Python）")
print()

# 检查期望的虚拟环境路径
expected_venv = r"F:\web_projects\mywebtest\backend\DjangoPermit\.venv\Scripts\python.exe"
if sys.executable.replace('\\', '/').lower() == expected_venv.replace('\\', '/').lower():
    print("✓ 使用的是正确的虚拟环境路径")
else:
    print("✗ 虚拟环境路径不匹配")
    print(f"期望路径: {expected_venv}")
    print(f"实际路径: {sys.executable}")
print()

# 检查已安装的包
try:
    import django
    print(f"✓ Django 版本: {django.__version__}")
except ImportError:
    print("✗ Django 未安装")

try:
    import rest_framework
    print(f"✓ Django REST Framework 已安装")
except ImportError:
    print("✗ Django REST Framework 未安装")

try:
    import pymysql
    print(f"✓ PyMySQL 已安装")
except ImportError:
    print("✗ PyMySQL 未安装")

print("=" * 60)

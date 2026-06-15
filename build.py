#!/usr/bin/env python3
"""
PyInstaller 打包脚本
将 main.py 打包成独立的 .exe 文件

使用方法:
    python build.py

生成的 .exe 文件将在 dist/ 文件夹中
"""

import PyInstaller.__main__
import os
import sys

def build_exe():
    """打包成 EXE"""
    print("🔨 开始打包...")
    print("=" * 50)
    
    # PyInstaller 参数
    args = [
        'main.py',
        '--name=ImageStitcher',  # 生成的程序名称
        '--onefile',  # 打包成单个 .exe 文件
        '--windowed',  # 无控制台窗口（GUI 应用）
        '--icon=icon.ico',  # 图标文件（如果存在）
        '--add-data=.',  # 包含当前目录的数据
        '-y',  # 覆盖输出目录（无需确认）
    ]
    
    # 检查图标文件
    if not os.path.exists('icon.ico'):
        print("⚠️  未找到 icon.ico，将使用默认图标")
        args.remove('--icon=icon.ico')
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 50)
        print("✓ 打包完成！")
        print("📁 .exe 文件位置: ./dist/ImageStitcher.exe")
        print("=" * 50)
    except Exception as e:
        print(f"✗ 打包失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()

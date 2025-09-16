#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import webbrowser
import subprocess
import time
import platform

def main():
    """启动Web界面的主函数"""
    parser = argparse.ArgumentParser(description='启动Subscription Converter Web界面')
    parser.add_argument('-p', '--port', type=int, default=8000, help='服务器端口')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    args = parser.parse_args()
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查必要的文件是否存在
    server_script = os.path.join(script_dir, 'web-ui', 'server.py')
    if not os.path.exists(server_script):
        print(f"错误：找不到服务器脚本 {server_script}")
        sys.exit(1)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误：需要Python 3.6或更高版本")
        sys.exit(1)
    
    # 启动服务器
    print(f"启动Web服务器，端口：{args.port}...")
    
    # 根据操作系统选择不同的启动方式
    if platform.system() == "Windows":
        server_process = subprocess.Popen(
            [sys.executable, server_script, '--port', str(args.port)],
            cwd=script_dir
        )
    else:
        server_process = subprocess.Popen(
            [sys.executable, server_script, '--port', str(args.port)],
            cwd=script_dir
        )
    
    # 等待服务器启动
    time.sleep(1)
    
    # 打开浏览器
    if not args.no_browser:
        url = f"http://localhost:{args.port}"
        print(f"在浏览器中打开：{url}")
        webbrowser.open(url)
    
    print("按 Ctrl+C 停止服务器")
    
    try:
        # 保持脚本运行
        server_process.wait()
    except KeyboardInterrupt:
        print("正在停止服务器...")
        server_process.terminate()
        server_process.wait()
        print("服务器已停止")

if __name__ == "__main__":
    main()
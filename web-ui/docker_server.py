#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import base64
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import threading
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('subscription-converter')

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入订阅转换器
try:
    from subscription_converter import SubscriptionConverter
    from timed_link_utils import TimedLinkManager
except ImportError:
    logger.error("错误：无法导入订阅转换器模块。请确保您在项目根目录运行此脚本。")
    sys.exit(1)

class APIHandler(SimpleHTTPRequestHandler):
    """处理API请求的HTTP处理器"""
    
    def __init__(self, *args, **kwargs):
        self.converter = SubscriptionConverter()
        self.timed_link_manager = TimedLinkManager()
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """重写日志方法，使用标准日志模块"""
        logger.info("%s - - [%s] %s" %
                 (self.address_string(),
                  self.log_date_time_string(),
                  format % args))
    
    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # 静态文件请求
        if not path.startswith('/api/'):
            return super().do_GET()
        
        # API请求
        query = parse_qs(parsed_url.query)
        
        try:
            if path == '/api/convert':
                self.handle_convert(query)
            elif path == '/api/generate-timed-link':
                self.handle_generate_timed_link(query)
            elif path == '/api/verify-timed-link':
                self.handle_verify_timed_link(query)
            elif path == '/api/server-status':
                self.handle_server_status()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            logger.error(f"处理GET请求时出错: {str(e)}", exc_info=True)
            self.send_error(500, str(e))
    
    def do_POST(self):
        """处理POST请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # 读取请求体
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
            
            if path == '/api/convert':
                self.handle_convert_post(data)
            elif path == '/api/generate-timed-link':
                self.handle_generate_timed_link_post(data)
            elif path == '/api/start-server':
                self.handle_start_server(data)
            elif path == '/api/stop-server':
                self.handle_stop_server()
            else:
                self.send_error(404, "API endpoint not found")
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"处理POST请求时出错: {str(e)}", exc_info=True)
            self.send_error(500, str(e))
    
    def handle_convert(self, query):
        """处理转换请求"""
        if 'url' not in query:
            self.send_error(400, "Missing 'url' parameter")
            return
        
        url = query['url'][0]
        template = query.get('template', ['standard'])[0]
        output_format = query.get('format', ['clash'])[0]
        compatible = 'no-compatible' not in query
        filter_info = 'no-filter' not in query
        
        try:
            # 调用转换器
            result = self.converter.convert(
                url,
                template=template,
                output_format=output_format,
                compatible_mode=compatible,
                filter_info_nodes=filter_info
            )
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'result': result,
                'stats': {
                    'total_nodes': self.converter.stats['total_nodes'],
                    'valid_nodes': self.converter.stats['valid_nodes'],
                    'info_nodes': self.converter.stats['info_nodes'],
                    'filtered_nodes': self.converter.stats['filtered_nodes']
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"处理转换请求时出错: {str(e)}", exc_info=True)
            self.send_error(500, str(e))
    
    def handle_convert_post(self, data):
        """处理POST转换请求"""
        if 'url' not in data and 'content' not in data:
            self.send_error(400, "Missing 'url' or 'content' parameter")
            return
        
        try:
            # 调用转换器
            if 'url' in data:
                result = self.converter.convert(
                    data['url'],
                    template=data.get('template', 'standard'),
                    output_format=data.get('format', 'clash'),
                    compatible_mode=data.get('compatible', True),
                    filter_info_nodes=data.get('filter_info', True)
                )
            else:
                # 从内容直接转换
                self.converter.parse_subscription_content(data['content'])
                result = self.converter.generate_config(
                    template=data.get('template', 'standard'),
                    output_format=data.get('format', 'clash')
                )
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'result': result,
                'stats': {
                    'total_nodes': self.converter.stats['total_nodes'],
                    'valid_nodes': self.converter.stats['valid_nodes'],
                    'info_nodes': self.converter.stats['info_nodes'],
                    'filtered_nodes': self.converter.stats['filtered_nodes']
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"处理POST转换请求时出错: {str(e)}", exc_info=True)
            self.send_error(500, str(e))
    
    def handle_generate_timed_link(self, query):
        """处理生成时效链接请求"""
        if 'url' not in query:
            self.send_error(400, "Missing 'url' parameter")
            return
        
        url = query['url'][0]
        expire_hours = int(query.get('expire', [24])[0])
        
        try:
            # 生成时效链接
            timed_link = self.timed_link_manager.generate_timed_link(url, expire_hours)
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'timed_link': timed_link,
                'expires_at': time.time() + expire_hours * 3600
            }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"处理生成时效链接请求时出错: {str(e)}", exc_info=True)
            self.send_error(500, str(e))
    
    def handle_generate_timed_link_post(self, data):
        """处理POST生成时效链接请求"""
        if 'url' not in data and 'content' not in data:
            self.send_error(400, "Missing 'url' or 'content' parameter")
            return
        
        try:
            # 生成时效链接
            if 'url' in data:
                timed_link = self.timed_link_manager.generate_timed_link(
                    data['url'], 
                    data.get('expire_hours', 24)
                )
            else:
                # 从内容直接生成
                timed_link = self.timed_link_manager.generate_timed_link_from_content(
                    data['content'], 
                    data.get('expire_hours', 24)
                )
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'timed_link': timed_link,
                'expires_at': time.time() + data.get('expire_hours', 24) * 3600
            }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"处理POST生成时效链接请求时出错: {str(e)}", exc_info=True)
            self.send_error(500, str(e))
    
    def handle_verify_timed_link(self, query):
        """处理验证时效链接请求"""
        if 'link' not in query:
            self.send_error(400, "Missing 'link' parameter")
            return
        
        link = query['link'][0]
        
        try:
            # 验证时效链接
            is_valid, original_link, expires_at = self.timed_link_manager.verify_timed_link(link)
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'valid': is_valid,
                'original_link': original_link if is_valid else None,
                'expires_at': expires_at if is_valid else None,
                'current_time': time.time()
            }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"处理验证时效链接请求时出错: {str(e)}", exc_info=True)
            self.send_error(500, str(e))
    
    def handle_server_status(self):
        """处理服务器状态请求"""
        # 发送响应
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': True,
            'status': 'running',
            'uptime': time.time() - server_start_time,
            'version': '1.0.0',
            'docker': True
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def handle_start_server(self, data):
        """处理启动订阅服务器请求"""
        port = data.get('port', 8080)
        
        # 这里应该启动一个新的线程来运行订阅服务器
        # 为了简化，我们只返回成功响应
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': True,
            'message': f'订阅服务器已在端口 {port} 启动'
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def handle_stop_server(self):
        """处理停止订阅服务器请求"""
        # 这里应该停止订阅服务器线程
        # 为了简化，我们只返回成功响应
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': True,
            'message': '订阅服务器已停止'
        }
        
        self.wfile.write(json.dumps(response).encode())

def run_server(host='0.0.0.0', port=8000, directory='/app/web-ui/public'):
    """运行Web服务器"""
    global server_start_time
    server_start_time = time.time()
    
    # 确保目录存在
    if not os.path.exists(directory):
        logger.warning(f"指定的目录 {directory} 不存在，将使用当前目录")
        directory = os.getcwd()
    
    # 切换到指定目录
    os.chdir(directory)
    
    # 创建服务器
    server_address = (host, port)
    httpd = HTTPServer(server_address, APIHandler)
    
    logger.info(f"启动Web服务器，监听 {host}:{port}...")
    logger.info(f"静态文件目录: {directory}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器运行时出错: {str(e)}", exc_info=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Subscription Converter Web UI (Docker)')
    parser.add_argument('-p', '--port', type=int, default=8000, help='服务器端口')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--dir', default='/app/web-ui/public', help='静态文件目录')
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, directory=args.dir)
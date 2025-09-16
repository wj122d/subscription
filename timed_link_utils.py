#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时效链接工具 - Timed Link Utils
用于生成和验证带有时效的订阅链接

作者: AI Assistant
版本: 1.0.0
"""

import base64
import time
import datetime
import hashlib
import urllib.parse
import json
import threading
import http.server
import socketserver
from typing import Dict, List, Any, Optional, Union

class TimedLinkManager:
    """时效链接管理器"""
    
    def __init__(self, secret_key: str = "subscription_converter_secret"):
        """初始化时效链接管理器
        
        Args:
            secret_key: 用于加密链接的密钥
        """
        self.secret_key = secret_key
        self.server = None
        self.server_thread = None
        self.proxies = []
    
    def generate_timed_link(self, ss_url: str, expire_hours: int = 24) -> str:
        """生成带时效的SS链接
        
        Args:
            ss_url: 原始SS链接
            expire_hours: 过期时间（小时）
            
        Returns:
            带时效的SS链接
        """
        if not ss_url.startswith('ss://'):
            raise ValueError("只支持SS链接")
        
        # 计算过期时间戳
        expire_time = int(time.time()) + expire_hours * 3600
        
        # 构建时效信息
        timed_info = {
            "original_url": ss_url,
            "expire_time": expire_time,
            "signature": self._generate_signature(ss_url, expire_time)
        }
        
        # 编码时效信息
        timed_info_str = json.dumps(timed_info)
        timed_info_b64 = base64.urlsafe_b64encode(timed_info_str.encode()).decode()
        
        # 构建带时效的链接
        return f"ss://time:{timed_info_b64}"
    
    def parse_timed_ss_url(self, timed_url: str) -> Optional[Dict[str, Any]]:
        """解析带时效的SS链接
        
        Args:
            timed_url: 带时效的SS链接
            
        Returns:
            解析后的时效信息，包含原始链接和过期时间
        """
        if not timed_url.startswith('ss://time:'):
            return None
        
        try:
            # 提取时效信息
            timed_info_b64 = timed_url[9:]  # 移除 'ss://time:' 前缀
            timed_info_str = base64.urlsafe_b64decode(timed_info_b64).decode()
            timed_info = json.loads(timed_info_str)
            
            # 验证签名
            original_url = timed_info.get('original_url')
            expire_time = timed_info.get('expire_time')
            signature = timed_info.get('signature')
            
            if not original_url or not expire_time or not signature:
                print("❌ 时效链接格式错误")
                return None
            
            # 验证签名
            expected_signature = self._generate_signature(original_url, expire_time)
            if signature != expected_signature:
                print("❌ 时效链接签名无效")
                return None
            
            # 添加可读的过期时间
            timed_info['expire_datetime'] = datetime.datetime.fromtimestamp(expire_time)
            
            return timed_info
        except Exception as e:
            print(f"❌ 解析时效链接失败: {e}")
            return None
    
    def verify_expiration(self, expire_time: int) -> bool:
        """验证链接是否过期
        
        Args:
            expire_time: 过期时间戳
            
        Returns:
            链接是否有效（未过期）
        """
        current_time = int(time.time())
        return current_time < expire_time
    
    def _generate_signature(self, url: str, expire_time: int) -> str:
        """生成签名
        
        Args:
            url: 原始链接
            expire_time: 过期时间戳
            
        Returns:
            签名字符串
        """
        signature_data = f"{url}{expire_time}{self.secret_key}"
        return hashlib.sha256(signature_data.encode()).hexdigest()[:16]
    
    def start_subscription_server(self, proxies: List[Dict[str, Any]], port: int = 8080) -> int:
        """启动订阅服务器
        
        Args:
            proxies: 代理节点列表
            port: 服务器端口
            
        Returns:
            实际使用的端口号
        """
        self.proxies = proxies
        
        # 创建自定义处理器
        timed_link_manager = self
        
        class SubscriptionHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    # 解析请求路径
                    if self.path.startswith('/sub'):
                        # 解析查询参数
                        query = urllib.parse.urlparse(self.path).query
                        params = dict(urllib.parse.parse_qsl(query))
                        
                        # 获取过期时间（小时）
                        expire_hours = int(params.get('expire', '24'))
                        
                        # 生成带时效的链接
                        timed_links = []
                        for proxy in timed_link_manager.proxies:
                            if proxy.get('type') == 'ss':
                                # 构建SS链接
                                method = proxy.get('cipher', 'aes-256-gcm')
                                password = proxy.get('password', '')
                                server = proxy.get('server', '')
                                port = proxy.get('port', 0)
                                name = proxy.get('name', server)
                                
                                user_info = f"{method}:{password}"
                                user_info_b64 = base64.urlsafe_b64encode(user_info.encode()).decode()
                                ss_url = f"ss://{user_info_b64}@{server}:{port}#{urllib.parse.quote(name)}"
                                
                                # 生成带时效的链接
                                timed_link = timed_link_manager.generate_timed_link(ss_url, expire_hours)
                                timed_links.append(timed_link)
                        
                        # 编码为Base64
                        content = '\n'.join(timed_links)
                        content_b64 = base64.b64encode(content.encode()).decode()
                        
                        # 发送响应
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/plain; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(content_b64.encode())
                    else:
                        # 发送404响应
                        self.send_response(404)
                        self.send_header('Content-Type', 'text/plain; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(b'Not Found')
                except Exception as e:
                    print(f"❌ 处理请求失败: {e}")
                    self.send_response(500)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(f"Internal Server Error: {str(e)}".encode())
            
            def log_message(self, format, *args):
                # 自定义日志格式
                print(f"📝 {self.client_address[0]} - {args[0]} {args[1]} {args[2]}")
        
        # 尝试启动服务器
        for attempt_port in range(port, port + 10):
            try:
                self.server = socketserver.ThreadingTCPServer(('0.0.0.0', attempt_port), SubscriptionHandler)
                self.server_thread = threading.Thread(target=self.server.serve_forever)
                self.server_thread.daemon = True
                self.server_thread.start()
                print(f"✅ 订阅服务器已启动，监听端口: {attempt_port}")
                return attempt_port
            except OSError:
                print(f"⚠️ 端口 {attempt_port} 已被占用，尝试下一个端口...")
        
        raise RuntimeError("无法启动服务器，所有尝试的端口都被占用")
    
    def stop_subscription_server(self):
        """停止订阅服务器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("✅ 订阅服务器已停止")
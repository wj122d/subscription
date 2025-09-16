#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订阅转换脚本 - Subscription Converter
支持多种协议和输出格式的订阅链接转换工具

作者: AI Assistant
版本: 1.1.0
"""

import base64
import urllib.parse
import urllib.request
import yaml
import json
import re
import argparse
import sys
import os
import time
import datetime
from typing import Dict, List, Any, Optional
from urllib.error import URLError, HTTPError
import uuid
import socket

# 导入时效链接工具
try:
    from timed_link_utils import TimedLinkManager
except ImportError:
    print("⚠️ 未找到时效链接工具模块，时效链接功能将不可用")
    TimedLinkManager = None

class SubscriptionConverter:
    """订阅转换器主类"""
    
    def __init__(self):
        self.proxies = []
        self.subscription_info = {}
        # 初始化时效链接管理器
        self.timed_link_manager = TimedLinkManager() if TimedLinkManager else None
        
    def fetch_subscription(self, url: str) -> str:
        """获取订阅内容"""
        try:
            print(f"正在获取订阅: {url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')
                print(f"✅ 订阅获取成功，内容长度: {len(content)}")
                return content
                
        except (URLError, HTTPError) as e:
            print(f"❌ 获取订阅失败: {e}")
            raise
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            raise
    
    def read_local_file(self, file_path: str) -> str:
        """读取本地文件内容"""
        try:
            print(f"正在读取本地文件: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ 文件读取成功，内容长度: {len(content)}")
                return content
                
        except FileNotFoundError:
            print(f"❌ 文件不存在: {file_path}")
            raise
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            raise
    
    def decode_base64_content(self, content: str) -> str:
        """解码base64内容"""
        try:
            # 尝试直接解码
            decoded = base64.b64decode(content).decode('utf-8')
            print("✅ Base64解码成功")
            return decoded
        except Exception as e:
            print(f"⚠️  Base64解码失败，尝试作为纯文本处理: {e}")
            return content
    
    def parse_hysteria2_url(self, url: str) -> Optional[Dict[str, Any]]:
        """解析Hysteria2 URL"""
        # hysteria2://password@server:port/?params#name
        match = re.match(r'hysteria2://([^@]+)@([^:]+):(\d+)/?\?(.*)#(.*)', url)
        if not match:
            return None
            
        password = match.group(1)
        server = match.group(2)
        port = int(match.group(3))
        params = match.group(4)
        name = urllib.parse.unquote(match.group(5))
        
        # 解析参数
        param_dict = {}
        for param in params.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                param_dict[key] = urllib.parse.unquote(value)
        
        return {
            'name': name,
            'type': 'hysteria2',
            'server': server,
            'port': port,
            'password': password,
            'skip-cert-verify': param_dict.get('insecure') == '1',
            'sni': param_dict.get('sni', server),
            'params': param_dict
        }
    
    def parse_vmess_url(self, url: str) -> Optional[Dict[str, Any]]:
        """解析VMess URL"""
        if not url.startswith('vmess://'):
            return None
            
        try:
            # 解码base64部分
            encoded = url[8:]  # 移除 'vmess://' 前缀
            
            # 自动添加padding
            missing_padding = len(encoded) % 4
            if missing_padding:
                encoded += '=' * (4 - missing_padding)
                
            decoded = base64.b64decode(encoded).decode('utf-8')
            config = json.loads(decoded)
            
            return {
                'name': config.get('ps', 'VMess节点'),
                'type': 'vmess',
                'server': config.get('add'),
                'port': int(config.get('port', 443)),
                'uuid': self.validate_and_fix_uuid(config.get('id', '')),
                'alterId': int(config.get('aid', 0)),
                'cipher': config.get('scy', 'auto'),
                'network': config.get('net', 'tcp'),
                'tls': config.get('tls') == 'tls',
                'ws-opts': {
                    'path': config.get('path', '/'),
                    'headers': {'Host': config.get('host', '')}
                } if config.get('net') == 'ws' else None
            }
        except Exception as e:
            print(f"⚠️  VMess URL解析失败: {e}")
            return None
    
    def parse_vless_url(self, url: str) -> Optional[Dict[str, Any]]:
        """解析VLESS URL"""
        if not url.startswith('vless://'):
            return None
            
        try:
            # vless://uuid@server:port?params#name
            match = re.match(r'vless://([^@]+)@([^:]+):(\d+)\?(.*)#(.*)', url)
            if not match:
                return None
                
            uuid = match.group(1)
            server = match.group(2)
            port = int(match.group(3))
            params = match.group(4)
            name = urllib.parse.unquote(match.group(5))
            
            # 解析参数
            param_dict = {}
            for param in params.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    param_dict[key] = urllib.parse.unquote(value)
            
            return {
                'name': name,
                'type': 'vless',
                'server': server,
                'port': port,
                'uuid': self.validate_and_fix_uuid(uuid),
                'network': param_dict.get('type', 'tcp'),
                'tls': param_dict.get('security') == 'tls',
                'flow': param_dict.get('flow', ''),
                'reality-opts': {
                    'public-key': param_dict.get('pbk', ''),
                    'short-id': param_dict.get('sid', '')
                } if param_dict.get('security') == 'reality' else None
            }
        except Exception as e:
            print(f"⚠️  VLESS URL解析失败: {e}")
            return None
    
    def parse_ss_url(self, url: str) -> Optional[Dict[str, Any]]:
        """解析Shadowsocks URL"""
        if not url.startswith('ss://'):
            return None
            
        try:
            # 检查是否是带时效的链接
            if url.startswith('ss://time:') and self.timed_link_manager:
                # 解析带时效的链接
                timed_info = self.timed_link_manager.parse_timed_ss_url(url)
                if timed_info:
                    # 验证链接是否过期
                    if not self.timed_link_manager.verify_expiration(timed_info['expire_time']):
                        print(f"⚠️  链接已过期，过期时间: {timed_info['expire_datetime']}")
                        return None
                    
                    # 解析原始SS链接
                    proxy = self.parse_ss_url(timed_info['original_url'])
                    if proxy:
                        # 添加过期时间信息
                        expire_datetime = timed_info['expire_datetime']
                        proxy['name'] = f"{proxy['name']} (到期: {expire_datetime.strftime('%Y-%m-%d %H:%M')})"
                        proxy['expire_time'] = timed_info['expire_time']
                        return proxy
                
                return None
            
            # ss://base64(method:password@server:port)#name
            content = url[5:]  # 移除 'ss://' 前缀
            
            # 分离名称部分
            if '#' in content:
                main_part, name = content.split('#', 1)
                name = urllib.parse.unquote(name)
            else:
                main_part = content
                name = 'SS节点'
            
            # 检查是否包含@符号（新格式 vs 旧格式）
            if '@' in main_part:
                # 新格式: auth@server:port
                auth_part, server_part = main_part.split('@', 1)
                
                if ':' in server_part:
                    server, port = server_part.split(':')
                else:
                    server = server_part
                    port = '443'
                
                # 解码认证信息
                try:
                    # 自动添加padding
                    missing_padding = len(auth_part) % 4
                    if missing_padding:
                        auth_part += '=' * (4 - missing_padding)
                    decoded_auth = base64.b64decode(auth_part).decode('utf-8')
                    if ':' in decoded_auth:
                        method, password = decoded_auth.split(':', 1)
                    else:
                        method = 'aes-256-gcm'
                        password = decoded_auth
                except:
                    # 如果不是base64编码，直接分割
                    if ':' in auth_part:
                        method, password = auth_part.split(':', 1)
                    else:
                        method = 'aes-256-gcm'
                        password = auth_part
            else:
                # 旧格式，整个main_part都是base64编码
                # 自动添加padding
                missing_padding = len(main_part) % 4
                if missing_padding:
                    main_part += '=' * (4 - missing_padding)
                    
                decoded = base64.b64decode(main_part).decode('utf-8')
                
                # 解析格式: method:password@server:port
                if '@' in decoded:
                    auth_server = decoded.split('@')
                    method_password = auth_server[0]
                    server_port = auth_server[1]
                    
                    if ':' in method_password:
                        method, password = method_password.split(':', 1)
                    else:
                        method = 'aes-256-gcm'
                        password = method_password
                        
                    if ':' in server_port:
                        server, port = server_port.split(':')
                    else:
                        server = server_port
                        port = '443'
                else:
                    # 格式不标准，尝试其他解析方式
                    parts = decoded.split(':')
                    if len(parts) >= 4:
                        method = parts[0]
                        password = parts[1]
                        server = parts[2]
                        port = parts[3]
                    else:
                        return None
            
            return {
                'name': name,
                'type': 'ss',
                'server': server,
                'port': int(port),
                'cipher': method,
                'password': password,
                'udp': True
            }
        except Exception as e:
            print(f"⚠️  SS URL解析失败: {e}")
            return None
    
    def parse_trojan_url(self, url: str) -> Optional[Dict[str, Any]]:
        """解析Trojan URL"""
        if not url.startswith('trojan://'):
            return None
            
        try:
            # trojan://password@server:port?params#name
            match = re.match(r'trojan://([^@]+)@([^:]+):(\d+)\??(.*?)#?(.*)', url)
            if not match:
                return None
                
            password = match.group(1)
            server = match.group(2)
            port = int(match.group(3))
            params = match.group(4)
            name = urllib.parse.unquote(match.group(5)) if match.group(5) else 'Trojan节点'
            
            # 解析参数
            param_dict = {}
            if params:
                for param in params.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        param_dict[key] = urllib.parse.unquote(value)
            
            return {
                'name': name,
                'type': 'trojan',
                'server': server,
                'port': port,
                'password': password,
                'skip-cert-verify': param_dict.get('allowInsecure') == '1',
                'sni': param_dict.get('sni', server)
            }
        except Exception as e:
            print(f"⚠️  Trojan URL解析失败: {e}")
            return None
    
    def filter_info_nodes(self, proxies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤掉信息节点（流量、到期时间等）"""
        filtered_proxies = []
        info_keywords = ['流量', '到期', '剩余', '套餐', '过期', 'GB', 'MB', 'TB', '天', '月', '年', 'expire', 'traffic', 'remain']
        
        for proxy in proxies:
            name = proxy['name'].lower()
            is_info_node = any(keyword in name for keyword in info_keywords)
            
            if not is_info_node:
                filtered_proxies.append(proxy)
            else:
                print(f"🗑️  过滤信息节点: {proxy['name']}")
        
        return filtered_proxies
    
    def parse_subscription_content(self, content: str) -> List[Dict[str, Any]]:
        """解析订阅内容"""
        proxies = []
        
        # 首先尝试base64解码
        decoded_content = self.decode_base64_content(content)
        
        # 按行分割
        lines = decoded_content.strip().split('\n')
        
        print(f"📋 开始解析 {len(lines)} 行内容")
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            print(f"🔍 解析第 {i} 行: {line[:50]}...")
            
            proxy = None
            
            # 根据协议类型解析
            if line.startswith('hysteria2://'):
                proxy = self.parse_hysteria2_url(line)
            elif line.startswith('vmess://'):
                proxy = self.parse_vmess_url(line)
            elif line.startswith('vless://'):
                proxy = self.parse_vless_url(line)
            elif line.startswith('ss://'):
                proxy = self.parse_ss_url(line)
            elif line.startswith('trojan://'):
                proxy = self.parse_trojan_url(line)
            else:
                print(f"⚠️  不支持的协议: {line[:20]}...")
                continue
            
            if proxy:
                proxies.append(proxy)
                print(f"✅ 成功解析: {proxy['name']} ({proxy['type']})")
            else:
                print(f"❌ 解析失败")
        
        print(f"🎉 总共解析成功 {len(proxies)} 个节点")
        return proxies
    
    def convert_hysteria2_to_vmess(self, proxies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将Hysteria2节点转换为VMess格式（用于兼容性）"""
        converted_proxies = []
        
        for proxy in proxies:
            if proxy['type'] == 'hysteria2':
                # 创建一个VMess代理作为替代
                vmess_proxy = {
                    'name': f"{proxy['name']} (VMess兼容)",
                    'type': 'vmess',
                    'server': proxy['server'],
                    'port': 443,  # 使用标准HTTPS端口
                    'uuid': self.validate_and_fix_uuid(proxy['password']),  # 使用原密码作为UUID
                    'alterId': 0,
                    'cipher': 'auto',
                    'network': 'ws',
                    'tls': True,
                    'skip-cert-verify': proxy.get('skip-cert-verify', True),
                    'ws-opts': {
                        'path': '/',
                        'headers': {'Host': proxy['server']}
                    }
                }
                converted_proxies.append(vmess_proxy)
                print(f"🔄 转换 Hysteria2 -> VMess: {proxy['name']}")
            else:
                converted_proxies.append(proxy)
        
        return converted_proxies
    
    def generate_clash_meta_config(self, proxies: List[Dict[str, Any]], 
                                 template: str = 'standard') -> Dict[str, Any]:
        """生成Clash Meta配置（支持更多协议）"""
        
        # Clash Meta基础配置
        base_config = {
            'port': 7890,
            'socks-port': 7891,
            'allow-lan': False,
            'mode': 'Rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            'dns': {
                'enable': True,
                'ipv6': False,
                'default-nameserver': ['223.5.5.5', '119.29.29.29'],
                'enhanced-mode': 'fake-ip',
                'fake-ip-range': '198.18.0.1/16',
                'nameserver': ['https://doh.pub/dns-query', 'https://dns.alidns.com/dns-query']
            },
            'geodata-mode': True,
            'geox-url': {
                'geoip': 'https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.dat',
                'geosite': 'https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geosite.dat'
            }
        }
        
        # 根据模板类型调整配置
        if template == 'minimal':
            config = {
                'port': 7890,
                'socks-port': 7891,
                'mode': 'Global',
                'proxies': proxies,
                'proxy-groups': [
                    {
                        'name': '🚀 代理选择',
                        'type': 'select',
                        'proxies': ['DIRECT'] + [p['name'] for p in proxies]
                    }
                ],
                'rules': ['MATCH,🚀 代理选择']
            }
        elif template == 'advanced':
            config = base_config.copy()
            config.update({
                'proxies': proxies,
                'proxy-groups': [
                    {
                        'name': '🚀 节点选择',
                        'type': 'select',
                        'proxies': ['♻️ 自动选择', '🔯 故障转移', '🔮 负载均衡', 'DIRECT'] + [p['name'] for p in proxies]
                    },
                    {
                        'name': '♻️ 自动选择',
                        'type': 'url-test',
                        'proxies': [p['name'] for p in proxies],
                        'url': 'http://www.gstatic.com/generate_204',
                        'interval': 300,
                        'tolerance': 50
                    },
                    {
                        'name': '🔯 故障转移',
                        'type': 'fallback',
                        'proxies': [p['name'] for p in proxies],
                        'url': 'http://www.gstatic.com/generate_204',
                        'interval': 300
                    },
                    {
                        'name': '🔮 负载均衡',
                        'type': 'load-balance',
                        'proxies': [p['name'] for p in proxies],
                        'url': 'http://www.gstatic.com/generate_204',
                        'interval': 300,
                        'strategy': 'consistent-hashing'
                    },
                    {
                        'name': '🎯 全球直连',
                        'type': 'select',
                        'proxies': ['DIRECT', '🚀 节点选择']
                    },
                    {
                        'name': '🛑 广告拦截',
                        'type': 'select',
                        'proxies': ['REJECT', 'DIRECT']
                    }
                ],
                'rules': [
                    'DOMAIN-SUFFIX,local,DIRECT',
                    'IP-CIDR,127.0.0.0/8,DIRECT',
                    'IP-CIDR,172.16.0.0/12,DIRECT',
                    'IP-CIDR,192.168.0.0/16,DIRECT',
                    'IP-CIDR,10.0.0.0/8,DIRECT',
                    'IP-CIDR,17.0.0.0/8,DIRECT',
                    'IP-CIDR,100.64.0.0/10,DIRECT',
                    'GEOIP,CN,🎯 全球直连',
                    'MATCH,🚀 节点选择'
                ]
            })
        else:
            config = base_config.copy()
            config.update({
                'proxies': proxies,
                'proxy-groups': [
                    {
                        'name': '🚀 节点选择',
                        'type': 'select',
                        'proxies': ['♻️ 自动选择', 'DIRECT'] + [p['name'] for p in proxies]
                    },
                    {
                        'name': '♻️ 自动选择',
                        'type': 'url-test',
                        'proxies': [p['name'] for p in proxies],
                        'url': 'http://www.gstatic.com/generate_204',
                        'interval': 300
                    }
                ],
                'rules': [
                    'DOMAIN-SUFFIX,local,DIRECT',
                    'IP-CIDR,127.0.0.0/8,DIRECT',
                    'IP-CIDR,172.16.0.0/12,DIRECT',
                    'IP-CIDR,192.168.0.0/16,DIRECT',
                    'IP-CIDR,10.0.0.0/8,DIRECT',
                    'GEOIP,CN,DIRECT',
                    'MATCH,🚀 节点选择'
                ]
            })
        
        return config
    
    def generate_clash_config(self, proxies: List[Dict[str, Any]], 
                            template: str = 'standard') -> Dict[str, Any]:
        """生成Clash配置"""
        
        # 基础配置模板
        base_config = {
            'port': 7890,
            'socks-port': 7891,
            'allow-lan': False,
            'mode': 'Rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            'dns': {
                'enable': True,
                'ipv6': False,
                'default-nameserver': ['223.5.5.5', '119.29.29.29'],
                'enhanced-mode': 'fake-ip',
                'fake-ip-range': '198.18.0.1/16',
                'nameserver': ['https://doh.pub/dns-query', 'https://dns.alidns.com/dns-query']
            }
        }
        
        # 根据模板类型调整配置
        if template == 'minimal':
            # 最小化配置
            config = {
                'port': 7890,
                'socks-port': 7891,
                'mode': 'Global',
                'proxies': proxies,
                'proxy-groups': [
                    {
                        'name': '🚀 代理选择',
                        'type': 'select',
                        'proxies': ['DIRECT'] + [p['name'] for p in proxies]
                    }
                ],
                'rules': ['MATCH,🚀 代理选择']
            }
        elif template == 'advanced':
            # 高级配置
            config = base_config.copy()
            config.update({
                'proxies': proxies,
                'proxy-groups': [
                    {
                        'name': '🚀 节点选择',
                        'type': 'select',
                        'proxies': ['♻️ 自动选择', '🔯 故障转移', '🔮 负载均衡', 'DIRECT'] + [p['name'] for p in proxies]
                    },
                    {
                        'name': '♻️ 自动选择',
                        'type': 'url-test',
                        'proxies': [p['name'] for p in proxies],
                        'url': 'http://www.gstatic.com/generate_204',
                        'interval': 300
                    },
                    {
                        'name': '🔯 故障转移',
                        'type': 'fallback',
                        'proxies': [p['name'] for p in proxies],
                        'url': 'http://www.gstatic.com/generate_204',
                        'interval': 300
                    },
                    {
                        'name': '🔮 负载均衡',
                        'type': 'load-balance',
                        'proxies': [p['name'] for p in proxies],
                        'url': 'http://www.gstatic.com/generate_204',
                        'interval': 300
                    },
                    {
                        'name': '🎯 全球直连',
                        'type': 'select',
                        'proxies': ['DIRECT', '🚀 节点选择']
                    },
                    {
                        'name': '🛑 广告拦截',
                        'type': 'select',
                        'proxies': ['REJECT', 'DIRECT']
                    }
                ],
                'rules': [
                    'DOMAIN-SUFFIX,local,DIRECT',
                    'IP-CIDR,127.0.0.0/8,DIRECT',
                    'IP-CIDR,172.16.0.0/12,DIRECT',
                    'IP-CIDR,192.168.0.0/16,DIRECT',
                    'IP-CIDR,10.0.0.0/8,DIRECT',
                    'IP-CIDR,17.0.0.0/8,DIRECT',
                    'IP-CIDR,100.64.0.0/10,DIRECT',
                    'GEOIP,CN,🎯 全球直连',
                    'MATCH,🚀 节点选择'
                ]
            })
        else:
            # 标准配置
            config = base_config.copy()
            config.update({
                'proxies': proxies,
                'proxy-groups': [
                    {
                        'name': '🚀 节点选择',
                        'type': 'select',
                        'proxies': ['♻️ 自动选择', 'DIRECT'] + [p['name'] for p in proxies]
                    },
                    {
                        'name': '♻️ 自动选择',
                        'type': 'url-test',
                        'proxies': [p['name'] for p in proxies],
                        'url': 'http://www.gstatic.com/generate_204',
                        'interval': 300
                    }
                ],
                'rules': [
                    'DOMAIN-SUFFIX,local,DIRECT',
                    'IP-CIDR,127.0.0.0/8,DIRECT',
                    'IP-CIDR,172.16.0.0/12,DIRECT',
                    'IP-CIDR,192.168.0.0/16,DIRECT',
                    'IP-CIDR,10.0.0.0/8,DIRECT',
                    'GEOIP,CN,DIRECT',
                    'MATCH,🚀 节点选择'
                ]
            })
        
        return config
    
    def generate_v2ray_config(self, proxies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成V2Ray配置"""
        
        # 转换代理为V2Ray格式
        outbounds = []
        
        for proxy in proxies:
            if proxy['type'] == 'vmess':
                outbound = {
                    "tag": proxy['name'],
                    "protocol": "vmess",
                    "settings": {
                        "vnext": [{
                            "address": proxy['server'],
                            "port": proxy['port'],
                            "users": [{
                                "id": proxy['uuid'],
                                "alterId": proxy.get('alterId', 0),
                                "security": proxy.get('cipher', 'auto')
                            }]
                        }]
                    },
                    "streamSettings": {
                        "network": proxy.get('network', 'tcp')
                    }
                }
                
                if proxy.get('tls'):
                    outbound["streamSettings"]["security"] = "tls"
                    
                outbounds.append(outbound)
        
        config = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "tag": "socks",
                    "port": 1080,
                    "protocol": "socks",
                    "settings": {
                        "auth": "noauth",
                        "udp": True
                    }
                },
                {
                    "tag": "http",
                    "port": 1087,
                    "protocol": "http"
                }
            ],
            "outbounds": [
                {
                    "tag": "proxy",
                    "protocol": "freedom"
                }
            ] + outbounds,
            "routing": {
                "rules": [
                    {
                        "type": "field",
                        "ip": ["geoip:private"],
                        "outboundTag": "direct"
                    }
                ]
            }
        }
        
        return config
    
    def save_config(self, config: Dict[str, Any], filename: str, format_type: str):
        """保存配置文件"""
        try:
            if format_type.lower() == 'yaml':
                with open(filename, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            elif format_type.lower() == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 配置文件已保存: {filename}")
            
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            raise
    
    def convert_subscription(self, url: str, output_format: str = 'clash', 
                           template: str = 'standard', output_file: str = None,
                           filter_info: bool = True, compatible_mode: bool = True, limit: int = None,
                           from_file: bool = False):
        """转换订阅链接"""
        try:
            # 获取订阅内容
            if from_file:
                content = self.read_local_file(url)
            else:
                content = self.fetch_subscription(url)
            
            # 解析代理节点
            self.proxies = self.parse_subscription_content(content)
            
            if not self.proxies:
                print("❌ 没有解析到任何有效的代理节点")
                return
            
            # 过滤掉信息节点
            if filter_info:
                self.proxies = self.filter_info_nodes(self.proxies)
            
            # 兼容模式：转换Hysteria2节点为VMess格式
            if compatible_mode:
                print("🔧 启用兼容模式，转换不支持的协议...")
                self.proxies = self.convert_hysteria2_to_vmess(self.proxies)
            
            # 限制节点数量
            if limit and len(self.proxies) > limit:
                print(f"📊 限制节点数量为 {limit} 个（原有 {len(self.proxies)} 个）")
                self.proxies = self.proxies[:limit]
            
            # 确保节点名称唯一
            print("🔍 检查并修复重复的节点名称...")
            self.proxies = self.ensure_unique_names(self.proxies)
            
            # 生成配置
            if output_format.lower() == 'clash':
                if compatible_mode:
                    config = self.generate_clash_config(self.proxies, template)
                else:
                    config = self.generate_clash_meta_config(self.proxies, template)
                file_ext = 'yaml'
            elif output_format.lower() == 'v2ray':
                config = self.generate_v2ray_config(self.proxies)
                file_ext = 'json'
            else:
                raise ValueError(f"不支持的输出格式: {output_format}")
            
            # 确定输出文件名
            if not output_file:
                if compatible_mode:
                    output_file = f"compatible_config.{file_ext}"
                else:
                    output_file = f"converted_config.{file_ext}"
            
            # 保存配置
            self.save_config(config, output_file, file_ext)
            
            # 显示统计信息
            self.print_statistics()
            
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            raise
    
    def print_statistics(self):
        """打印统计信息"""
        print("\n" + "="*50)
        print("📊 转换统计信息")
        print("="*50)
        
        # 按协议类型统计
        protocol_count = {}
        for proxy in self.proxies:
            protocol = proxy['type']
            protocol_count[protocol] = protocol_count.get(protocol, 0) + 1
        
        print(f"总节点数: {len(self.proxies)}")
        print("\n协议分布:")
        for protocol, count in protocol_count.items():
            print(f"  {protocol.upper()}: {count} 个")
        
        print("\n节点列表:")
        for i, proxy in enumerate(self.proxies, 1):
            print(f"  {i:2d}. {proxy['name']} ({proxy['type'].upper()}) - {proxy['server']}:{proxy['port']}")
        
        print("="*50)

    def validate_and_fix_uuid(self, uuid_str: str) -> str:
        """验证并修复UUID格式"""
        if not uuid_str:
            return str(uuid.uuid4())
        
        # 移除所有非字母数字字符
        clean_uuid = re.sub(r'[^a-fA-F0-9]', '', uuid_str)
        
        # 如果长度不是32位，生成新的UUID
        if len(clean_uuid) != 32:
            print(f"⚠️  UUID格式不正确: {uuid_str}，生成新UUID")
            return str(uuid.uuid4())
        
        # 格式化为标准UUID格式
        try:
            formatted_uuid = f"{clean_uuid[:8]}-{clean_uuid[8:12]}-{clean_uuid[12:16]}-{clean_uuid[16:20]}-{clean_uuid[20:32]}"
            # 验证是否为有效UUID
            uuid.UUID(formatted_uuid)
            return formatted_uuid
        except ValueError:
            print(f"⚠️  UUID格式不正确: {uuid_str}，生成新UUID")
            return str(uuid.uuid4())

    def ensure_unique_names(self, proxies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """确保节点名称唯一"""
        name_count = {}
        unique_proxies = []
        
        for proxy in proxies:
            original_name = proxy['name']
            
            # 如果名称已存在，添加数字后缀
            if original_name in name_count:
                name_count[original_name] += 1
                proxy['name'] = f"{original_name} {name_count[original_name]}"
            else:
                name_count[original_name] = 0
            
            unique_proxies.append(proxy)
            
        return unique_proxies

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='订阅转换工具')
    parser.add_argument('url', nargs='?', help='订阅链接URL或本地文件路径')
    parser.add_argument('-f', '--format', choices=['clash', 'v2ray'], 
                       default='clash', help='输出格式 (默认: clash)')
    parser.add_argument('-t', '--template', choices=['minimal', 'standard', 'advanced'], 
                       default='standard', help='配置模板 (默认: standard)')
    parser.add_argument('-o', '--output', help='输出文件名')
    parser.add_argument('--test', action='store_true', help='测试模式，使用内置示例')
    parser.add_argument('--no-filter', action='store_true', help='不过滤信息节点（流量、到期时间等）')
    parser.add_argument('--compatible', action='store_true', default=True, help='兼容模式，转换不支持的协议为兼容格式（默认启用）')
    parser.add_argument('--no-compatible', action='store_true', help='禁用兼容模式，保持原始协议')
    parser.add_argument('--limit', type=int, help='限制节点数量（避免配置文件过大）')
    parser.add_argument('--file', action='store_true', help='从本地文件读取节点内容')
    parser.add_argument('--generate-timed', action='store_true', help='生成带时效的SS链接')
    parser.add_argument('--expire', type=int, default=24, help='链接过期时间（小时）')
    parser.add_argument('--server', action='store_true', help='启动订阅服务器')
    parser.add_argument('--port', type=int, default=8080, help='订阅服务器端口')
    
    args = parser.parse_args()
    
    converter = SubscriptionConverter()
    
    try:
        # 检查时效链接功能是否可用
        if (args.generate_timed or args.server) and not converter.timed_link_manager:
            parser.error("时效链接功能不可用，请确保timed_link_utils.py文件存在")
        
        # 启动订阅服务器模式
        if args.server:
            print("🌐 启动订阅服务器模式")
            
            # 首先需要加载节点
            if args.url:
                if args.file:
                    content = converter.read_local_file(args.url)
                else:
                    content = converter.fetch_subscription(args.url)
                
                converter.proxies = converter.parse_subscription_content(content)
                
                if not converter.proxies:
                    print("❌ 没有解析到任何有效的代理节点")
                    return
                
                # 过滤信息节点
                if not args.no_filter:
                    converter.proxies = converter.filter_info_nodes(converter.proxies)
                
                # 启动服务器
                port = converter.timed_link_manager.start_subscription_server(converter.proxies, args.port)
                
                # 显示订阅链接
                local_ip = socket.gethostbyname(socket.gethostname())
                print(f"
📋 订阅链接:")
                print(f"http://localhost:{port}/sub?expire={args.expire}")
                print(f"http://{local_ip}:{port}/sub?expire={args.expire}")
                print("
使用方法:")
                print(f"1. 将上述链接添加到代理客户端作为订阅")
                print(f"2. 链接中的节点将在 {args.expire} 小时后过期")
                print(f"3. 可以通过修改 expire 参数调整过期时间")
                
                # 保持程序运行
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("
⚠️  用户中断，停止服务器...")
                    converter.timed_link_manager.stop_subscription_server()
                
                return
            else:
                parser.error("启动服务器模式需要提供订阅链接URL或本地文件")
        
        # 生成带时效的链接模式
        elif args.generate_timed:
            if not args.url:
                parser.error("需要提供SS链接或包含SS链接的文件")
            
            if args.file:
                # 从文件读取SS链接
                content = converter.read_local_file(args.url)
                lines = content.strip().split('
')
                
                timed_links = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('ss://'):
                        try:
                            timed_link = converter.timed_link_manager.generate_timed_link(line, args.expire)
                            timed_links.append(timed_link)
                            print(f"✅ 生成时效链接: {timed_link[:50]}...")
                        except Exception as e:
                            print(f"❌ 生成时效链接失败: {e}")
                
                # 保存到文件
                output_file = args.output or "timed_links.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('
'.join(timed_links))
                
                print(f"✅ 已生成 {len(timed_links)} 个带时效的链接，保存到 {output_file}")
                print(f"⏰ 链接将在 {args.expire} 小时后过期")
            else:
                # 直接处理单个SS链接
                if args.url.startswith('ss://'):
                    try:
                        timed_link = converter.timed_link_manager.generate_timed_link(args.url, args.expire)
                        print(f"✅ 生成的时效链接: {timed_link}")
                        print(f"⏰ 链接将在 {args.expire} 小时后过期")
                        
                        if args.output:
                            with open(args.output, 'w', encoding='utf-8') as f:
                                f.write(timed_link)
                            print(f"✅ 链接已保存到 {args.output}")
                    except Exception as e:
                        print(f"❌ 生成时效链接失败: {e}")
                else:
                    parser.error("URL必须是SS链接，以ss://开头")
        
        # 测试模式
        elif args.test:
            # 检查参数
            if not args.test and not args.url:
                parser.error("需要提供订阅链接URL，或使用 --test 进行测试")
                
            print("🧪 测试模式：使用内置示例")
            test_content = """aHlzdGVyaWEyOi8vNDJhY2EwNzAtNDllYy00MGMzLTg0OWYtYmRkZGRiMjc2MWZmQGRpd3U2NC5kaTVqaS5sYXQ6MjY1MDAvP2luc2VjdXJlPTEmc25pPWRpd3U2NC5kaTVqaS5sYXQjJUU3JUJFJThFJUU1JTlCJUJEDQpoeXN0ZXJpYTI6Ly80MmFjYTA3MC00OWVjLTQwYzMtODQ5Zi1iZGRkZGIyNzYxZmZAZGl3dTM0LmRpNWppLmxhdDoyNjcwMC8/aW5zZWN1cmU9MSZzbmk9ZGl3dTM0LmRpNWppLmxhdCMlRTklQTYlOTklRTYlQjglQUY="""
            
            proxies = converter.parse_subscription_content(test_content)
            converter.proxies = proxies
            
            # 过滤信息节点
            if not args.no_filter:
                converter.proxies = converter.filter_info_nodes(converter.proxies)
            
            # 处理兼容模式参数
            compatible_mode = args.compatible and not args.no_compatible
            
            # 兼容模式
            if compatible_mode:
                print("🔧 启用兼容模式，转换不支持的协议...")
                converter.proxies = converter.convert_hysteria2_to_vmess(converter.proxies)
            
            if args.format.lower() == 'clash':
                if compatible_mode:
                    config = converter.generate_clash_config(converter.proxies, args.template)
                else:
                    config = converter.generate_clash_meta_config(converter.proxies, args.template)
                file_ext = 'yaml'
            else:
                config = converter.generate_v2ray_config(converter.proxies)
                file_ext = 'json'
            
            if args.compatible:
                output_file = args.output or f"test_compatible_config.{file_ext}"
            else:
                output_file = args.output or f"test_config.{file_ext}"
            converter.save_config(config, output_file, file_ext)
            converter.print_statistics()
        else:
            # 正常转换模式
            if not args.url:
                parser.error("需要提供订阅链接URL")
                
            # 处理兼容模式参数
            compatible_mode = args.compatible and not args.no_compatible
            converter.convert_subscription(args.url, args.format, args.template, args.output, not args.no_filter, compatible_mode, args.limit, args.file)
            
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
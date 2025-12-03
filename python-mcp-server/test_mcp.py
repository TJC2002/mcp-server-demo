#!/usr/bin/env python3
"""
MCP服务器测试脚本

按照正确的MCP协议流程测试服务器：
1. 发送initialize请求
2. 发送tools/list请求
3. 发送tools/call请求
"""

import json
import sys

# MCP协议测试消息序列
messages = [
    # 1. 初始化请求
    {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "initialize",
        "params": {
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            },
            "capabilities": {}
        }
    },
    # 2. 列出工具请求
    {
        "jsonrpc": "2.0",
        "id": "2",
        "method": "tools/list"
    },
    # 3. 调用工具请求
    {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "tools/call",
        "params": {
            "name": "downloadReport",
            "arguments": {
                "date": "2025-12-04"
            }
        }
    }
]

# 将所有消息转换为JSON字符串，每个消息占一行
for msg in messages:
    print(json.dumps(msg))
    # 刷新输出，确保消息立即发送
    sys.stdout.flush()

#!/usr/bin/env python3
"""
远程MCP服务器 - 下载报表工具

这个MCP服务帮助用户下载CSV数据报表。
支持根据日期下载销售报表。
"""

import json
import asyncio
from typing import Any
import base64
import re
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions
import mcp.server.stdio

# 创建服务器实例
server = Server("remote-report-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    列出可用的工具。
    
    提供downloadReport工具，用于下载指定日期的销售报表。
    """
    return [
        types.Tool(
            name="downloadReport",
            description="下载指定日期的销售报表",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "报表日期，格式为YYYY-MM-DD",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    }
                },
                "required": ["date"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """
    处理工具调用。
    
    根据工具名称处理不同的工具调用，返回相应的内容。
    """
    if not arguments:
        return [
            types.TextContent(
                type="text",
                text="错误：缺少工具参数"
            )
        ]
    
    if name == "downloadReport":
        # 下载报表
        date = arguments.get("date")
        
        if not date:
            return [
                types.TextContent(
                    type="text",
                    text="错误：缺少日期参数"
                )
            ]
        
        # 验证日期格式
        date_regex = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_regex, date):
            return [
                types.TextContent(
                    type="text",
                    text="错误：日期格式无效，请使用YYYY-MM-DD格式"
                )
            ]
        
        try:
            # 生成模拟报表内容
            report_content = f"日期: {date}\n\n销售报表\n\n产品名称,销售额\n产品A,1000.00\n产品B,2000.00\n产品C,1500.00\n\n总计,4500.00"
            
            # 创建报表文件的Base64编码
            base64_content = base64.b64encode(report_content.encode()).decode()
            
            # 返回包含文件信息的响应
            return [
                types.TextContent(
                    type="text",
                    text=f"已生成{date}的销售报表\n\n" +
                          f"文件名: report-{date}.csv\n" +
                          f"文件类型: text/csv\n" +
                          f"文件内容(BASE64): {base64_content}"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"生成报表失败: {str(e)}"
                )
            ]
    
    else:
        return [
            types.TextContent(
                type="text",
                text=f"未知工具: {name}"
            )
        ]


async def main():
    """运行服务器"""
    print("启动远程MCP服务器...")
    print("使用stdio模式，通过管道进行通信")
    print("\n可用工具:")
    print("- downloadReport: 下载指定日期的销售报表")
    print("\n示例调用:")
    print('{"jsonrpc": "2.0", "id": "1", "method": "listTools"}')
    print('{"jsonrpc": "2.0", "id": "2", "method": "callTool", "params": {"name": "downloadReport", "arguments": {"date": "2025-12-04"}}}}')
    
    # 初始化服务器选项
    init_options = InitializationOptions(
        server_name="remote-report-server",
        server_version="1.0.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )
    
    try:
        # 使用stdio运行服务器
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                init_options,
            )
    except KeyboardInterrupt:
        print("\n服务器正在关闭...")
    except Exception as e:
        print(f"服务器运行失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
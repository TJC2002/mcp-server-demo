#!/usr/bin/env python3
"""
测试客户端 - 用于测试MCP服务器
"""

import asyncio
from mcp.client import Client

async def main():
    """
    测试MCP服务器
    """
    # 创建客户端实例
    client = Client()
    
    try:
        # 连接到服务器（通过stdin/stdout）
        print("连接到MCP服务器...")
        
        # 列出可用工具
        tools = await client.list_tools()
        print(f"\n可用工具: {len(tools)}个")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        
        # 调用downloadReport工具
        print("\n调用downloadReport工具...")
        result = await client.call_tool(
            name="downloadReport",
            arguments={"date": "2025-12-04"}
        )
        
        print("\n工具调用结果:")
        for content in result:
            if content.type == "text":
                print(f"文本内容: {content.text}")
            else:
                print(f"其他类型内容: {content.type}")
    
    except Exception as e:
        print(f"测试失败: {str(e)}")
    finally:
        # 关闭客户端
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
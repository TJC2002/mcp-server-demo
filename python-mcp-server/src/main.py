from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import base64
import re
import asyncio
import json

app = FastAPI(title="Remote MCP Server")

# MCP协议相关模型
class ToolParam(BaseModel):
    type: str
    description: str = None

class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ToolParam]

class ToolCall(BaseModel):
    tool: str
    params: Dict[str, Any]

class ContentItem(BaseModel):
    type: str
    text: str = None
    file: Dict[str, Any] = None

class ToolResponse(BaseModel):
    content: List[ContentItem]

# 工具定义
TOOLS = {
    "downloadReport": {
        "description": "下载指定日期的销售报表",
        "parameters": {
            "date": {
                "type": "string",
                "description": "报表日期，格式为YYYY-MM-DD"
            }
        }
    }
}

@app.get("/mcp/tools")
def get_tools():
    """获取可用工具列表"""
    return {"tools": TOOLS}

@app.post("/mcp/call")
def call_tool(tool_call: ToolCall):
    """调用工具"""
    tool_name = tool_call.tool
    params = tool_call.params
    
    if tool_name not in TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
    
    if tool_name == "downloadReport":
        date = params.get("date")
        if not date:
            return ToolResponse(
                content=[
                    ContentItem(type="text", text="错误：缺少日期参数")
                ]
            )
        
        # 验证日期格式
        date_regex = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_regex, date):
            return ToolResponse(
                content=[
                    ContentItem(type="text", text="错误：日期格式无效，请使用YYYY-MM-DD格式")
                ]
            )
        
        # 生成模拟报表内容
        report_content = f"日期: {date}\n\n销售报表\n\n产品名称,销售额\n产品A,1000.00\n产品B,2000.00\n产品C,1500.00\n\n总计,4500.00"
        
        # 创建报表文件的Base64编码
        base64_content = base64.b64encode(report_content.encode()).decode()
        
        # 返回包含文件的响应
        return ToolResponse(
            content=[
                ContentItem(
                    type="file",
                    file={
                        "name": f"report-{date}.csv",
                        "mimeType": "text/csv",
                        "content": base64_content,
                        "encoding": "base64"
                    }
                ),
                ContentItem(
                    type="text",
                    text=f"已生成{date}的销售报表"
                )
            ]
        )
    
    return ToolResponse(
        content=[
            ContentItem(type="text", text=f"Tool {tool_name} called with params: {params}")
        ]
    )

@app.get("/")
def root():
    """根路径"""
    return {"message": "Remote MCP Server is running"}

# SSE端点支持
@app.get("/sse")
async def sse_endpoint():
    """SSE连接端点"""
    async def event_generator():
        # 发送初始连接确认
        yield f'data: {json.dumps({"type": "connected", "message": "SSE connected"})}\n\n'
        
        # 保持连接
        while True:
            await asyncio.sleep(30)  # 每30秒发送一次心跳
            yield f'data: {json.dumps({"type": "heartbeat"})}\n\n'
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/sse/message")
async def sse_message(message: Dict[str, Any]):
    """SSE消息端点"""
    # 这里可以添加消息处理逻辑
    return {"status": "received", "message": message}

if __name__ == "__main__":
    import uvicorn
    import json
    uvicorn.run(app, host="0.0.0.0", port=8000)
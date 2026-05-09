"""
WebSocket 对话端点

提供实时流式对话功能
"""
import json
import asyncio
from typing import Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.agents.pet_health_agent import PetHealthAgent

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
    db: Session = Depends(get_db),
) -> None:
    """
    WebSocket 流式对话接口
    
    - 支持实时消息传输
    - 保持长连接状态
    - 自动维护对话上下文
    - 支持心跳检测和断线重连
    
    消息格式:
    {
        "type": "message" | "heartbeat" | "error",
        "data": {
            "conversation_id": "可选",
            "pet_id": "可选",
            "message": "用户消息",
            ...
        }
    }
    """
    user = None
    try:
        await websocket.accept()
        
        # 接收初始认证消息
        init_data = await websocket.receive_json()
        
        if init_data.get("type") != "auth":
            await websocket.send_json({
                "type": "error",
                "message": "需要先进行身份认证"
            })
            await websocket.close()
            return
        
        token = init_data.get("token")
        if not token:
            await websocket.send_json({
                "type": "error",
                "message": "缺少认证令牌"
            })
            await websocket.close()
            return
        
        from src.core.security import decode_token
        payload = decode_token(token)
        if not payload:
            await websocket.send_json({
                "type": "error",
                "message": "无效的认证令牌"
            })
            await websocket.close()
            return
        
        user_id = payload.get("sub")
        if not user_id:
            await websocket.send_json({
                "type": "error",
                "message": "无法解析用户信息"
            })
            await websocket.close()
            return
        
        from src.db.crud.user import get_user_by_id
        user = get_user_by_id(db, user_id)
        if not user:
            await websocket.send_json({
                "type": "error",
                "message": "用户不存在"
            })
            await websocket.close()
            return
        
        # 连接成功，发送确认消息
        await manager.connect(websocket, user_id)
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "message": "连接成功"
        })
        
        # 初始化Agent
        agent = PetHealthAgent(
            db=db,
            user_id=user_id
        )
        
        # 持续监听消息
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0  # 心跳超时时间
                )
                
                msg_type = data.get("type")
                
                if msg_type == "heartbeat":
                    # 响应心跳
                    await websocket.send_json({"type": "heartbeat", "status": "ok"})
                    continue
                
                elif msg_type == "message":
                    # 处理用户消息
                    message_data = data.get("data", {})
                    user_message = message_data.get("message", "")
                    conversation_id = message_data.get("conversation_id")
                    pet_id = message_data.get("pet_id")
                    
                    if not user_message:
                        await websocket.send_json({
                            "type": "error",
                            "message": "消息内容不能为空"
                        })
                        continue
                    
                    # 发送处理中状态
                    await websocket.send_json({
                        "type": "processing",
                        "conversation_id": conversation_id,
                        "message": "正在思考..."
                    })
                    
                    try:
                        # 调用Agent处理
                        result = agent.chat(
                            user_input=user_message,
                            conversation_id=conversation_id,
                            pet_id=pet_id
                        )
                        
                        # 发送响应结果
                        await websocket.send_json({
                            "type": "response",
                            "data": {
                                "conversation_id": result["conversation_id"],
                                "response": result["response"],
                                "relevant_context": result.get("relevant_context", [])
                            }
                        })
                        
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"处理失败: {str(e)}"
                        })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "未知的消息类型"
                    })
                    
            except asyncio.TimeoutError:
                # 超时发送心跳
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break
                    
    except WebSocketDisconnect:
        print(f"用户 {user_id} 断开WebSocket连接")
        
    except Exception as e:
        print(f"WebSocket错误: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"服务器错误: {str(e)}"
            })
        except:
            pass
            
    finally:
        if user:
            manager.disconnect(user.user_id)

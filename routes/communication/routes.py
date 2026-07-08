# from fastapi import APIRouter, Depends, HTTPException, status

# from app.auth import login_required
# from applications.communication.models import ChatSession, Message, Notification
# from applications.communication.schema import (
#     ChatSessionCreate,
#     ChatSessionUpdate,
#     MessageCreate,
#     MessageUpdate,
#     NotificationCreate,
#     NotificationUpdate,
#     serialize_chat_session,
#     serialize_message,
#     serialize_notification,
# )
# from applications.user.models import User

# router = APIRouter(tags=["Communication"])


# def _payload(data, fk_map: dict[str, str]) -> dict:
#     raw = data.model_dump(exclude_unset=True)
#     for source, target in fk_map.items():
#         if source in raw:
#             raw[target] = raw.pop(source)
#     return raw


# async def _get_or_404(model, resource_id: int, label: str):
#     instance = await model.get_or_none(id=resource_id)
#     if not instance:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} not found")
#     return instance


# @router.post("/messages")
# async def create_message(data: MessageCreate, current_user: User = Depends(login_required)):
#     item = await Message.create(**_payload(data, {"from_user_id": "from_user_id", "to_user_id": "to_user_id"}))
#     return {"message": "Message created successfully", "data": serialize_message(item)}


# @router.get("/messages")
# async def list_messages(current_user: User = Depends(login_required)):
#     return [serialize_message(item) for item in await Message.all().order_by("-created_at")]


# @router.get("/messages/{message_id}")
# async def get_message(message_id: int, current_user: User = Depends(login_required)):
#     return serialize_message(await _get_or_404(Message, message_id, "Message"))


# @router.patch("/messages/{message_id}")
# async def update_message(message_id: int, data: MessageUpdate, current_user: User = Depends(login_required)):
#     item = await _get_or_404(Message, message_id, "Message")
#     await Message.filter(id=item.id).update(**_payload(data, {"from_user_id": "from_user_id", "to_user_id": "to_user_id"}))
#     return {"message": "Message updated successfully", "data": serialize_message(await Message.get(id=item.id))}


# @router.delete("/messages/{message_id}")
# async def delete_message(message_id: int, current_user: User = Depends(login_required)):
#     item = await _get_or_404(Message, message_id, "Message")
#     await item.delete()
#     return {"message": "Message deleted successfully"}


# @router.post("/chat-sessions")
# async def create_chat_session(data: ChatSessionCreate, current_user: User = Depends(login_required)):
#     item = await ChatSession.create(**_payload(data, {"user1_id": "user1_id", "user2_id": "user2_id"}))
#     return {"message": "Chat session created successfully", "data": serialize_chat_session(item)}


# @router.get("/chat-sessions")
# async def list_chat_sessions(current_user: User = Depends(login_required)):
#     return [serialize_chat_session(item) for item in await ChatSession.all().order_by("-updated_at")]


# @router.get("/chat-sessions/{session_id}")
# async def get_chat_session(session_id: int, current_user: User = Depends(login_required)):
#     return serialize_chat_session(await _get_or_404(ChatSession, session_id, "Chat session"))


# @router.patch("/chat-sessions/{session_id}")
# async def update_chat_session(session_id: int, data: ChatSessionUpdate, current_user: User = Depends(login_required)):
#     item = await _get_or_404(ChatSession, session_id, "Chat session")
#     await ChatSession.filter(id=item.id).update(**_payload(data, {"user1_id": "user1_id", "user2_id": "user2_id"}))
#     return {"message": "Chat session updated successfully", "data": serialize_chat_session(await ChatSession.get(id=item.id))}


# @router.delete("/chat-sessions/{session_id}")
# async def delete_chat_session(session_id: int, current_user: User = Depends(login_required)):
#     item = await _get_or_404(ChatSession, session_id, "Chat session")
#     await item.delete()
#     return {"message": "Chat session deleted successfully"}


# @router.post("/notifications")
# async def create_notification(data: NotificationCreate, current_user: User = Depends(login_required)):
#     item = await Notification.create(**_payload(data, {"user_id": "user_id"}))
#     return {"message": "Notification created successfully", "data": serialize_notification(item)}


# @router.get("/notifications")
# async def list_notifications(current_user: User = Depends(login_required)):
#     return [serialize_notification(item) for item in await Notification.all().order_by("-created_at")]


# @router.get("/notifications/{notification_id}")
# async def get_notification(notification_id: int, current_user: User = Depends(login_required)):
#     return serialize_notification(await _get_or_404(Notification, notification_id, "Notification"))


# @router.patch("/notifications/{notification_id}")
# async def update_notification(notification_id: int, data: NotificationUpdate, current_user: User = Depends(login_required)):
#     item = await _get_or_404(Notification, notification_id, "Notification")
#     await Notification.filter(id=item.id).update(**_payload(data, {"user_id": "user_id"}))
#     return {"message": "Notification updated successfully", "data": serialize_notification(await Notification.get(id=item.id))}


# @router.delete("/notifications/{notification_id}")
# async def delete_notification(notification_id: int, current_user: User = Depends(login_required)):
#     item = await _get_or_404(Notification, notification_id, "Notification")
#     await item.delete()
#     return {"message": "Notification deleted successfully"}

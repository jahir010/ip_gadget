from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from applications.communication.models import ChatSession, Message, Notification


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    from_user_id: UUID
    from_name: Optional[str] = None
    to_user_id: UUID
    to_name: Optional[str] = None
    text: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    is_read: Optional[bool] = False
    is_delivered: Optional[bool] = False
    is_deleted: Optional[bool] = False
    edited_at: Optional[datetime] = None
    reactions: List[dict] = Field(default_factory=list)


class MessageUpdate(BaseModel):
    from_user_id: Optional[UUID] = None
    from_name: Optional[str] = None
    to_user_id: Optional[UUID] = None
    to_name: Optional[str] = None
    text: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    is_read: Optional[bool] = None
    is_delivered: Optional[bool] = None
    is_deleted: Optional[bool] = None
    edited_at: Optional[datetime] = None
    reactions: Optional[List[dict]] = None


class ChatSessionCreate(BaseModel):
    user1_id: UUID
    user2_id: UUID
    is_active: Optional[bool] = True
    last_message_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class ChatSessionUpdate(BaseModel):
    user1_id: Optional[UUID] = None
    user2_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    last_message_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class NotificationCreate(BaseModel):
    user_id: UUID
    title: Optional[str] = None
    body: Optional[str] = None
    is_read: Optional[bool] = False


class NotificationUpdate(BaseModel):
    user_id: Optional[UUID] = None
    title: Optional[str] = None
    body: Optional[str] = None
    is_read: Optional[bool] = None


class MessageOut(ORMBase):
    id: int
    from_user_id: UUID
    from_name: Optional[str]
    to_user_id: UUID
    to_name: Optional[str]
    text: Optional[str]
    media_type: Optional[str]
    media_url: Optional[str]
    is_read: bool
    is_delivered: bool
    is_deleted: bool
    edited_at: Optional[datetime]
    reactions: List[dict]
    created_at: datetime


class ChatSessionOut(ORMBase):
    id: int
    user1_id: UUID
    user2_id: UUID
    is_active: bool
    last_message_at: Optional[datetime]
    ended_at: Optional[datetime]
    updated_at: datetime
    created_at: datetime


class NotificationOut(ORMBase):
    id: int
    user_id: UUID
    title: Optional[str]
    body: Optional[str]
    is_read: bool
    created_at: datetime


def serialize_message(instance: Message) -> MessageOut:
    return MessageOut.model_validate(
        {
            "id": instance.id,
            "from_user_id": instance.from_user_id,
            "from_name": instance.from_name,
            "to_user_id": instance.to_user_id,
            "to_name": instance.to_name,
            "text": instance.text,
            "media_type": instance.media_type,
            "media_url": instance.media_url,
            "is_read": instance.is_read,
            "is_delivered": instance.is_delivered,
            "is_deleted": instance.is_deleted,
            "edited_at": instance.edited_at,
            "reactions": instance.reactions or [],
            "created_at": instance.created_at,
        }
    )


def serialize_chat_session(instance: ChatSession) -> ChatSessionOut:
    return ChatSessionOut.model_validate(
        {
            "id": instance.id,
            "user1_id": instance.user1_id,
            "user2_id": instance.user2_id,
            "is_active": instance.is_active,
            "last_message_at": instance.last_message_at,
            "ended_at": instance.ended_at,
            "updated_at": instance.updated_at,
            "created_at": instance.created_at,
        }
    )


def serialize_notification(instance: Notification) -> NotificationOut:
    return NotificationOut.model_validate(
        {
            "id": instance.id,
            "user_id": instance.user_id,
            "title": instance.title,
            "body": instance.body,
            "is_read": instance.is_read,
            "created_at": instance.created_at,
        }
    )

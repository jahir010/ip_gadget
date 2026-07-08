from tortoise import fields, models


# class Message(models.Model):
#     id = fields.IntField(pk=True)
#     from_user = fields.ForeignKeyField("models.User", related_name="sent_messages", on_delete=fields.CASCADE)
#     from_name = fields.CharField(max_length=255, null=True)
#     to_user = fields.ForeignKeyField("models.User", related_name="received_messages", on_delete=fields.CASCADE)
#     to_name = fields.CharField(max_length=255, null=True)
#     text = fields.TextField(null=True)
#     media_type = fields.CharField(max_length=100, null=True)
#     media_url = fields.CharField(max_length=500, null=True)
#     is_read = fields.BooleanField(default=False)
#     is_delivered = fields.BooleanField(default=False)
#     is_deleted = fields.BooleanField(default=False)
#     edited_at = fields.DatetimeField(null=True)
#     reactions = fields.JSONField(default=list)
#     created_at = fields.DatetimeField(auto_now_add=True)

#     class Meta:
#         table = "Messages"
#         ordering = ["-created_at"]


# class ChatSession(models.Model):
#     id = fields.IntField(pk=True)
#     user1 = fields.ForeignKeyField("models.User", related_name="chat_sessions_started", on_delete=fields.CASCADE)
#     user2 = fields.ForeignKeyField("models.User", related_name="chat_sessions_joined", on_delete=fields.CASCADE)
#     is_active = fields.BooleanField(default=True)
#     last_message_at = fields.DatetimeField(null=True)
#     ended_at = fields.DatetimeField(null=True)
#     updated_at = fields.DatetimeField(auto_now=True)
#     created_at = fields.DatetimeField(auto_now_add=True)

#     class Meta:
#         table = "chat_session"
#         ordering = ["-updated_at"]


# class Notification(models.Model):
#     id = fields.IntField(pk=True)
#     user = fields.ForeignKeyField("models.User", related_name="notifications", on_delete=fields.CASCADE)
#     title = fields.CharField(max_length=255, null=True)
#     body = fields.TextField(null=True)
#     is_read = fields.BooleanField(default=False)
#     created_at = fields.DatetimeField(auto_now_add=True)

#     class Meta:
#         table = "notifications"
#         ordering = ["-created_at"]




class ChatMessage(models.Model):
    """Store all chat messages persistently"""
    id = fields.IntField(pk=True)
    
    # Sender info  # "riders", "customers", "vendors", "admins"
    from_id = fields.CharField(max_length=100)   # User ID
    from_name = fields.CharField(max_length=255, null=True)  # Display name
    
    # Recipient info
    to_id = fields.CharField(max_length=100)
    
    # Message content
    text = fields.TextField(null=True)
    message_id = fields.CharField(max_length=100, unique=True)  # UUID for idempotency
    media_type = fields.CharField(max_length=20, null=True)  # "image", etc.
    media_url = fields.CharField(max_length=500, null=True)
    
    # Status tracking
    is_read = fields.BooleanField(default=False)
    is_delivered = fields.BooleanField(default=False)
    is_deleted = fields.BooleanField(default=False)
    edited_at = fields.DatetimeField(null=True)
    reactions = fields.JSONField(default=dict)  # {"👍": ["installers:123", "customers:456"]}
    
    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "chat_messages"
        indexes = [
            ["from_id", "to_id", "created_at"],
            ["to_id", "is_read"],
        ]
    
    def __str__(self):
        return f"{self.from_id} -> {self.to_id}: {self.text[:50] if self.text else 'Media'}"
    

class ChatSession(models.Model):
    """Track active chat sessions between users"""
    id = fields.IntField(pk=True)
    
    # User 1
    user1_id = fields.CharField(max_length=100)
    
    # User 2
    user2_id = fields.CharField(max_length=100)
    
    # Session state
    is_active = fields.BooleanField(default=True)
    last_message_at = fields.DatetimeField(null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    ended_at = fields.DatetimeField(null=True)
    
    class Meta:
        table = "chat_sessions"
        unique_together = [["user1_id","user2_id"]]
        indexes = [
            ["user1_id", "is_active"],
            ["user2_id", "is_active"],
        ]


class OfflineNotification(models.Model):
    """Store notifications for offline users"""
    id = fields.IntField(pk=True)
    
    # Recipient
    to_id = fields.CharField(max_length=100)
    
    # Notification content
    notification_id = fields.CharField(max_length=100, unique=True)
    title = fields.CharField(max_length=255)
    body = fields.TextField()
    
    # Metadata
    data = fields.JSONField(default={})
    urgency = fields.CharField(max_length=20, default="normal")  # low, normal, high, critical
    
    # Status
    is_delivered = fields.BooleanField(default=False)
    delivered_at = fields.DatetimeField(null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField()  # Auto-delete after 30 days
    
    class Meta:
        table = "offline_notifications"
        indexes = [
            ["to_id", "is_delivered"],
            ["expires_at"],
        ]
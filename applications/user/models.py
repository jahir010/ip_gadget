from enum import Enum

from passlib.context import CryptContext
from tortoise import fields, models
import uuid

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

class UserRole(str, Enum):
    STAFF = "STAFF"
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"


class Permission(models.Model):
    id = fields.IntField(pk=True, readonly=True, hidden=True)
    name = fields.CharField(max_length=100, unique=True, editable=False)
    codename = fields.CharField(max_length=100, unique=True, editable=False)

    def __str__(self):
        return self.codename


class Group(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)

    permissions: fields.ManyToManyRelation["Permission"] = fields.ManyToManyField(
        "models.Permission",
        related_name="groups",
        through="group_permissions",
    )

    def __str__(self):
        return self.name


class User(models.Model):
    id = fields.UUIDField(pk=True, editable=False, hidden=True)
    email = fields.CharField(max_length=120, null=True, unique=True)
    password = fields.CharField(max_length=2000, default="")
    name = fields.CharField(max_length=100, null=True)
    phone = fields.CharField(max_length=15, null=True, unique=True)
    photo = fields.CharField(max_length=400, null=True)

    role = fields.CharEnumField(UserRole, default=None, null=True, blank=True)
    is_active_2fa = fields.BooleanField(default=False)

    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    groups: fields.ManyToManyRelation["Group"] = fields.ManyToManyField(
        "models.Group",
        related_name="users",
        through="user_groups",
    )
    user_permissions: fields.ManyToManyRelation["Permission"] = fields.ManyToManyField(
        "models.Permission",
        related_name="users",
        through="user_permissions",
    )

    class Meta:
        table = "users"

    @classmethod
    def set_password(cls, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        if not self.password:
            return False
        try:
            return pwd_context.verify(password, self.password)
        except Exception:
            return False

    def __str__(self):
        display = self.email or f"user-{self.id}"
        return f"{display}"

    async def has_permission(self, codename: str) -> bool:
        if self.is_superuser:
            return True

        await self.fetch_related("user_permissions", "groups__permissions")

        for perm in self.user_permissions:
            if perm.codename == codename:
                return True

        for group in self.groups:
            for perm in group.permissions:
                if perm.codename == codename:
                    return True
        return False

    async def save(self, *args, **kwargs):
        await super().save(*args, **kwargs)

class BannedType(str, Enum):
    HOURS24 = "HOURS24"
    DAYS7 = "DAYS7"
    PERMANENT = "PERMANENT"

class IsBanned(models.Model):
    user = fields.OneToOneField("models.User", related_name="user")
    banned_type = fields.CharEnumField(BannedType, default=BannedType.HOURS24)
    banned_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "isBanned"




class PushNotification(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="notifications")
    title = fields.CharField(max_length=255, null=True)
    body = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_read = fields.BooleanField(default=False)

    class Meta:
        table = "notifications"

class NotificationSetting(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="notification_settings")
    is_enabled = fields.BooleanField(default=True)

    class Meta:
        table = "notification_settings"

class DeviceToken(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    token = fields.CharField(max_length=256)
    platform = fields.CharField(max_length=32)
    created_at = fields.DatetimeField(auto_now_add=True)

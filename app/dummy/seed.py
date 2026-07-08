from datetime import datetime, timedelta, timezone
from applications.communication.models import ChatSession
from applications.site.models import CookiesPolicy, Policy, SiteReview, Terms
from applications.user.models import Group, Permission, User, UserRole
from app.dummy.users import create_test_users


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def _ensure_user(
    *,
    email: str,
    password: str,
    name: str,
    role: UserRole,
    is_superuser: bool = False,
    is_active: bool = True,
) -> User:
    defaults = {
        "name": name,
        "role": role,
        "is_superuser": is_superuser,
        "is_active": is_active,
        "password": User.set_password(password),
    }
    user, created = await User.get_or_create(email=email, defaults=defaults)
    updated = created is False

    if updated:
        dirty = False
        for field, value in defaults.items():
            if field == "password":
                if not user.verify_password(password):
                    user.password = value
                    dirty = True
                continue
            if getattr(user, field) != value:
                setattr(user, field, value)
                dirty = True
        if dirty:
            await user.save()
    return user


async def _ensure_group_with_permissions(name: str, codenames: list[str]) -> Group:
    group, _ = await Group.get_or_create(name=name)
    permissions = await Permission.filter(codename__in=codenames)
    await group.permissions.clear()
    if permissions:
        await group.permissions.add(*permissions)
    return group


async def _seed_users() -> dict[str, User]:
    await create_test_users()
    admin = await _ensure_user(
        email="admin@gmail.com",
        password="admin",
        name="Admin User",
        is_superuser=True,
    )
    merchant = await _ensure_user(
        email="merchant@example.com",
        password="merchant123",
        name="Mona Merchant",
        role=UserRole.STAFF,
    )
    va = await _ensure_user(
        email="va@example.com",
        password="va123456",
        name="Victor Assistant",
        role=UserRole.STAFF,
    )
    support = await _ensure_user(
        email="support@example.com",
        password="support123",
        name="Sara Support",
        role=UserRole.STAFF,
    )

    admin_group = await _ensure_group_with_permissions(
        "Admins",
        [
            "view_user",
            "add_user",
            "update_user",
            "delete_user",
            "view_group",
            "add_group",
            "update_group",
            "delete_group",
            "view_permission",
        ],
    )
    support_group = await _ensure_group_with_permissions(
        "Support",
        ["view_user", "update_user", "view_permission"],
    )

    await admin.groups.clear()
    await admin.groups.add(admin_group)
    await support.groups.clear()
    await support.groups.add(support_group)

    return {
        "admin": admin,
        "merchant": merchant,
        "va": va,
        "support": support,
    }





# async def _seed_communication(users: dict[str, User]) -> dict[str, object]:
#     now = _utc_now()
#     session, _ = await ChatSession.get_or_create(
#         user1=users["merchant"],
#         user2=users["va"],
#         defaults={
#             "is_active": True,
#             "last_message_at": now,
#         },
#     )
#     message, _ = await Message.get_or_create(
#         from_user=users["merchant"],
#         to_user=users["va"],
#         text="Can you share a timeline for the listing work?",
#         defaults={
#             "from_name": "Mona Merchant",
#             "to_name": "Victor Assistant",
#             "is_delivered": True,
#             "reactions": [{"emoji": "thumbs_up", "by": str(users["va"].id)}],
#         },
#     )
#     notification, _ = await Notification.get_or_create(
#         user=users["va"],
#         title="New project message",
#         defaults={
#             "body": "You have a new message from Mona Merchant.",
#             "is_read": False,
#         },
#     )
#     return {
#         "chat_session": session,
#         "message": message,
#         "notification": notification,
#     }




async def _seed_site(users: dict[str, User]) -> dict[str, object]:
    terms, _ = await Terms.get_or_create(
        title="Platform Terms",
        defaults={"details": "Sample terms and conditions for development use."},
    )
    policy, _ = await Policy.get_or_create(
        title="Privacy Policy",
        defaults={"details": "Sample privacy policy for development use."},
    )
    cookies, _ = await CookiesPolicy.get_or_create(
        title="Cookies Policy",
        defaults={"details": "Sample cookies policy for development use."},
    )
    site_review, _ = await SiteReview.get_or_create(
        user=users["support"],
        defaults={
            "rating": 5,
            "comment": "Helpful workflows and clear API structure.",
        },
    )
    return {
        "terms": terms,
        "policy": policy,
        "cookies_policy": cookies,
        "site_review": site_review,
    }


async def seed_all_dummy_data() -> None:
    users = await _seed_users()
    site = await _seed_site(users)

    print(
        "[dummy] seeding completed "
        f"(users={len(users)}, "
        #f"communication={len(communication)}, feedback={len(feedback)}, site={len(site)})"
    )

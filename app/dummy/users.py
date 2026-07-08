from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from applications.user.models import User, UserRole

USERS_DATA = [
    {
        "email": "admin@gmail.com",
        "password": "admin",
        "name": "Admin User",
        "role": UserRole.ADMIN,
        "is_superuser": True,
        "is_active": True,
        "is_active_2fa": False,
    },
    {
        "email": "staff@gmail.com",
        "password": "staff",
        "name": "Staff User",
        "role": UserRole.STAFF,
        "is_staff": True,
        "is_active": True,
        "is_active_2fa": False,
    },
    {
        "email": "m1@gmail.com",
        "password": "user",
        "name": "STAF User 1",
        "role": UserRole.STAFF,
        "is_active": True,
        "is_active_2fa": False,
    },
    {
        "email": "m2@gmail.com",
        "password": "user",
        "name": "STAF User 2",
        "role": UserRole.STAFF,
        "is_active": True,
        "is_active_2fa": False,
    },
    {
        "email": "m3@gmail.com",
        "password": "user",
        "name": "STAF User 3",
        "role": UserRole.STAFF,
        "is_active": True,
        "is_active_2fa": True,
    },
    {
        "email": "v1@gmail.com",
        "password": "user",
        "name": "CUSTOMER Assistant 1",
        "role": UserRole.CUSTOMER,
        "is_active": True,
        "is_active_2fa": False,
    },
    {
        "email": "v2@gmail.com",
        "password": "user",
        "name": "CUSTOMER Assistant 2",
        "role": UserRole.CUSTOMER,
        "is_active": True,
        "is_active_2fa": False,
    },
    {
        "email": "v3@gmail.com",
        "password": "user",
        "name": "CUSTOMER Assistant 3",
        "role": UserRole.CUSTOMER,
        "is_active": True,
        "is_active_2fa": True,
    },
]


async def create_test_users():
    created_count = 0
    updated_count = 0
    for data in USERS_DATA:
        email = data["email"]
        try:
            async with in_transaction() as conn:
                defaults = {
                    "email": email,
                    "name": data.get("name"),
                    "role": data.get("role", UserRole.STAFF),
                    "is_active": data.get("is_active", True),
                    "is_superuser": data.get("is_superuser", False),
                    "is_active_2fa": data.get("is_active_2fa", False),
                    "password": User.set_password(data["password"]),
                }

                user, created = await User.get_or_create(
                    email=email,
                    defaults=defaults,
                    using_db=conn,
                )

                if created:
                    created_count += 1
                    print(f"[dummy-user] created: {email}")
                    continue

                updated = False
                for field in ["name", "role", "is_active", "is_superuser", "is_active_2fa"]:
                    expected = defaults[field]
                    if getattr(user, field) != expected:
                        setattr(user, field, expected)
                        updated = True

                # Keep seeded credentials deterministic so login always works.
                password_valid = False
                if user.password:
                    try:
                        password_valid = user.verify_password(data["password"])
                    except Exception:
                        password_valid = False

                if not password_valid:
                    user.password = defaults["password"]
                    updated = True

                if updated:
                    await user.save(using_db=conn)
                    updated_count += 1
                    print(f"[dummy-user] updated: {email}")
                else:
                    print(f"[dummy-user] exists: {email}")
        except IntegrityError as error:
            print(f"[dummy-user] integrity error for {email}: {error}")
        except Exception as error:
            print(f"[dummy-user] unexpected error for {email}: {error}")

    print(f"[dummy-user] seeding completed (created={created_count}, updated={updated_count})")

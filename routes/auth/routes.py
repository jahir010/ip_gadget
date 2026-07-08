from typing import Optional
import re

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from applications.user.models import User, UserRole
from applications.user.schema import ensure_user_not_banned
from app.token import get_current_user, create_access_token, create_refresh_token
from app.utils.otp_manager import generate_otp, verify_otp, verify_session_key
from app.config import settings
router = APIRouter()


# ------------------------
# Helpers
# ------------------------
async def detect_input_type(value: str) -> str:
    value = value.strip()
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if re.match(email_regex, value):
        return "email"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid email address",
    )


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _build_token_data(user: User) -> dict:
    return {
        "sub": str(user.id),
        "email": user.email or "",
        "role": user.role,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


# ------------------------
# LOGIN (OAuth2)
# ------------------------
@router.post("/login_auth2", response_model=TokenResponse)
async def login_auth2(form_data: OAuth2PasswordRequestForm = Depends()):
    email = _normalize_email(form_data.username)
    await detect_input_type(email)

    user = await User.get_or_none(email=email)

    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token_data = _build_token_data(user)
    await ensure_user_not_banned(user)

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
    }


# ------------------------
# LOGIN WITH OTP SUPPORT
# ------------------------
@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    otp_value: Optional[str] = Form(None),
):
    email = _normalize_email(email)
    await detect_input_type(email)

    user = await User.get_or_none(email=email)
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    await ensure_user_not_banned(user)

    # OPTIONAL OTP FLAG (if you add later)
    if getattr(user, "is_active_2fa", True):
        normalized_otp = otp_value.strip() if otp_value else None
        if not normalized_otp:
            otp = await generate_otp(email, "login")
            return {
                "status": "otp_required",
                "message": f"OTP sent to {email} { '(DEBUG MODE: OTP is ' + otp + ')' if settings.DEBUG else '' }",
                "purpose": "login",
            }

        await verify_otp(email, normalized_otp, "login")

    token_data = _build_token_data(user)

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
        "role": user.role,
    }


# ------------------------
# SEND OTP
# ------------------------
@router.post("/send_otp", description="""
    ### 👤 Dummy Users

    1.  Email: admin@gmail.com
        Password: admin
        Role: ADMIN

    2.  Email: staff@gmail.com
        Password: staff
        Role: STAFF

    3.  Email: m1@gmail.com
        Password: user
        Role: MERCHANT

    4.  Email: m2@gmail.com
        Password: user
        Role: MERCHANT

    5.  Email: m3@gmail.com
        Password: user
        Role: MERCHANT
        2FA: Enabled

    6.  Email: v1@gmail.com
        Password: user
        Role: VIRTUAL_ASSISTANT

    7.  Email: v2@gmail.com
        Password: user
        Role: VIRTUAL_ASSISTANT

    8.  Email: v3@gmail.com
        Password: user
        Role: VIRTUAL_ASSISTANT
        2FA: Enabled

    ---

    Notes:
    - These users are created when dummy seeding is enabled.
    - `/send_otp` with `purpose=signup` should use an unregistered email.
    - Existing users are useful for login and forgot_password testing.
""")
async def send_otp(
    email: str = Form(...),
    purpose: str = Form("signup", description="Purpose of OTP: signup, forgot_password, login"),
):
    email = _normalize_email(email)
    await detect_input_type(email)
    purpose = purpose.strip().lower()

    user = await User.get_or_none(email=email)

    allowed_purposes = {"signup", "forgot_password", "login"}
    if purpose not in allowed_purposes:
        raise HTTPException(status_code=400, detail="Invalid OTP purpose")

    if purpose == "signup" and user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if purpose in {"forgot_password", "login"} and not user:
        raise HTTPException(status_code=400, detail="User not found")

    if purpose == "login" and user and getattr(user, "is_active_2fa", False):
        raise HTTPException(status_code=400, detail="OTP login is not enabled for this user")

    otp = await generate_otp(email, purpose)

    return {
        "status": "success",
        "message": f"OTP sent to {email} { '(DEBUG MODE: OTP is ' + otp + ')' if settings.DEBUG else '' }",
        "purpose": purpose,
    }


# ------------------------
# SIGNUP
# ------------------------
@router.post("/signup")
async def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    otp_value: str = Form(...),
    role: UserRole = Form(...),
):
    email = _normalize_email(email)
    await detect_input_type(email)

    name = name.strip()
    password = password.strip()
    otp_value = otp_value.strip()

    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    await verify_otp(email, otp_value, "signup")

    if await User.get_or_none(email=email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await User.create(
        first_name=name,
        email=email,
        password=User.set_password(password),
        role=role,
        is_active=True,
    )

    token_data = _build_token_data(user)

    return {
        "message": "User created successfully",
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
        "role": user.role,
    }


# ------------------------
# VERIFY OTP
# ------------------------
@router.post("/verify_otp")
async def verify_otp_route(
    email: str = Form(...),
    otp_value: str = Form(...),
    purpose: str = Form(...),
):
    email = _normalize_email(email)
    await detect_input_type(email)
    session_key = await verify_otp(email, otp_value, purpose)

    return {
        "status": "success",
        "sessionKey": session_key,
    }


# ------------------------
# RESET PASSWORD (LOGGED IN)
# ------------------------
@router.post("/reset_password")
async def reset_password(
    user: User = Depends(get_current_user),
    old_password: str = Form(...),
    new_password: str = Form(...),
):
    new_password = new_password.strip()
    if not user.verify_password(old_password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    if not new_password:
        raise HTTPException(status_code=400, detail="New password is required")
    if old_password == new_password:
        raise HTTPException(status_code=400, detail="New password must be different from old password")

    user.password = User.set_password(new_password)
    await user.save()

    return {"message": "Password updated successfully"}


# ------------------------
# FORGOT PASSWORD
# ------------------------
@router.post("/forgot_password")
async def forgot_password(
    email: str = Form(...),
    password: str = Form(...),
    session_key: str = Form(...),
):
    email = _normalize_email(email)
    await detect_input_type(email)
    password = password.strip()
    session_key = session_key.strip()

    user = await User.get_or_none(email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    await verify_session_key(email, session_key, "forgot_password")

    user.password = User.set_password(password)
    await user.save()

    return {"message": "Password reset successfully"}


# ------------------------
# VERIFY TOKEN
# ------------------------
@router.get("/verify-token")
async def verify_token(request: Request, user: User = Depends(get_current_user)):
    response = {
        "id": user.id,
        "email": user.email,
        "name": user.first_name,
        "role": user.role,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "photo": user.photo,
    }
    if hasattr(request.state, "new_tokens"):
        response["new_tokens"] = request.state.new_tokens
    return response

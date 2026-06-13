from fastapi import APIRouter, HTTPException, Response, Request, Depends
from app.models.student import StudentCreate, StudentLogin, StudentResponse, StudentInDB, TokenResponse
from app.db.database import get_collection
from app.core.config import settings
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson import ObjectId
import secrets
from app.utils import send_verification_email

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── HELPERS ───────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(student_id: str) -> str:
    return create_token(
        {"sub": student_id, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(student_id: str) -> str:
    return create_token(
        {"sub": student_id, "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

def create_email_token(student_id: str) -> str:
    return create_token(
        {"sub": student_id, "type": "email_verify"},
        timedelta(minutes=settings.EMAIL_VERIFY_TOKEN_EXPIRE_MINUTES)
    )

async def get_current_student(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        student_id = payload.get("sub")
        if not student_id or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    students = get_collection("students")
    student = await students.find_one({"_id": ObjectId(student_id)})
    if not student:
        raise HTTPException(status_code=401, detail="Student not found")
    return student

# ─── REGISTER ──────────────────────────────────────────────

@router.post("/register", status_code=201)
async def register(data: StudentCreate):
    students = get_collection("students")
    existing = await students.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    student_doc = StudentInDB(
        full_name=data.full_name,
        email=data.email,
        passwordHash=hash_password(data.password),
        school_level=data.school_level,
        age=data.age,
        state=data.state
    )
    result = await students.insert_one(student_doc.model_dump())
    student_id = str(result.inserted_id)
    verify_token = create_email_token(student_id)
    await send_verification_email(data.email, data.full_name, verify_token)
    return {
        "message": "Registration successful. Please check your email to verify your account."
    }

# ─── VERIFY EMAIL ──────────────────────────────────────────

@router.get("/verify-email")
async def verify_email(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        student_id = payload.get("sub")
        if payload.get("type") != "email_verify":
            raise HTTPException(status_code=400, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    students = get_collection("students")
    await students.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Email verified successfully"}

# ─── LOGIN ─────────────────────────────────────────────────

@router.post("/login")
async def login(data: StudentLogin, response: Response):
    students = get_collection("students")
    student = await students.find_one({"email": data.email})
    if not student:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if student.get("is_locked"):
        raise HTTPException(status_code=403, detail="Account locked. Contact support.")
    if not verify_password(data.password, student["passwordHash"]):
        failed = student.get("failed_attempts", 0) + 1
        update = {"failed_attempts": failed}
        if failed >= settings.MAX_LOGIN_ATTEMPTS:
            update["is_locked"] = True
        await students.update_one({"_id": student["_id"]}, {"$set": update})
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not student.get("is_verified"):
        raise HTTPException(status_code=403, detail="Please verify your email first")
    await students.update_one(
        {"_id": student["_id"]},
        {"$set": {"failed_attempts": 0, "updated_at": datetime.utcnow()}}
    )
    student_id = str(student["_id"])
    access_token = create_access_token(student_id)
    refresh_token = create_refresh_token(student_id)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return {
        "message": "Login successful",
        "student": {
            "id": student_id,
            "full_name": student["full_name"],
            "email": student["email"],
            "school_level": student["school_level"],
            "is_verified": student["is_verified"]
        }
    }

# ─── LOGOUT ────────────────────────────────────────────────

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

# ─── ME ────────────────────────────────────────────────────

@router.get("/me")
async def get_me(student=Depends(get_current_student)):
    return {
        "id": str(student["_id"]),
        "full_name": student["full_name"],
        "email": student["email"],
        "school_level": student["school_level"],
        "is_verified": student["is_verified"],
        "auth_provider": student.get("auth_provider", "local"),
        "created_at": student["created_at"]
    }

# ─── REFRESH TOKEN ─────────────────────────────────────────

@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        student_id = payload.get("sub")
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    new_access_token = create_access_token(student_id)
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return {"message": "Token refreshed"}

# ─── FORGOT PASSWORD ───────────────────────────────────────

@router.post("/forgot-password")
async def forgot_password(email: str):
    students = get_collection("students")
    student = await students.find_one({"email": email})
    if not student:
        return {"message": "If this email exists you will receive a reset link"}
    student_id = str(student["_id"])
    reset_token = create_token(
        {"sub": student_id, "type": "password_reset"},
        timedelta(minutes=30)
    )
    return {
        "message": "Password reset token generated",
        "reset_token": reset_token
    }

# ─── RESET PASSWORD ────────────────────────────────────────

@router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        student_id = payload.get("sub")
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    students = get_collection("students")
    await students.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": {
            "passwordHash": hash_password(new_password),
            "is_locked": False,
            "failed_attempts": 0,
            "updated_at": datetime.utcnow()
        }}
    )
    return {"message": "Password reset successful"}
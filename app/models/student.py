from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SchoolLevel(str, Enum):
    secondary = "secondary"
    university = "university"
    graduate = "graduate"
    working = "working"
    interested = "interested"

class AuthProvider(str, Enum):
    local = "local"
    google = "google"

class StudentCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v
    school_level: SchoolLevel
    age: Optional[int] = Field(None, ge=10, le=60)
    state: Optional[str] = None

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class StudentResponse(BaseModel):
    id: str
    full_name: str
    email: str
    school_level: str
    is_verified: bool
    auth_provider: str
    created_at: datetime

class StudentInDB(BaseModel):
    full_name: str
    email: str
    passwordHash: str
    school_level: str
    age: Optional[int] = None
    state: Optional[str] = None
    is_verified: bool = False
    is_locked: bool = False
    failed_attempts: int = 0
    auth_provider: str = "local"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ConversationState(str, Enum):
    identity = "identity"
    background = "background"
    strengths = "strengths"
    goals = "goals"
    reasoning = "reasoning"
    completed = "completed"
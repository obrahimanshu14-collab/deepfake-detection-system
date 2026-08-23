from pydantic import BaseModel, EmailStr


class UserSignup(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PredictionResponse(BaseModel):
    label: str
    confidence: float
    filename: str

class GoogleLoginRequest(BaseModel):
    credential: str    
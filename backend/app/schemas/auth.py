from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=200)
    name: str = Field(min_length=2, max_length=100)

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)

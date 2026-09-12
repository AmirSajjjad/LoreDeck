from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PublicUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    phone_number: str | None
    profile_pic: str | None
    name: str | None
    email: str | None
    telegram_id: int | None
    created_at: datetime


class AuthenticationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str
    expires_in: int
    user: PublicUserResponse

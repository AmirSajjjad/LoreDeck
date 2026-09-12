import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

E164_PHONE_NUMBER = re.compile(r"\+[1-9]\d{7,14}")


class SignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    phone_number: str | None = Field(default=None, max_length=16)
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("username must not be blank")
        return normalized

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("name", mode="before")
    @classmethod
    def trim_optional_strings(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        normalized = value.strip()
        if E164_PHONE_NUMBER.fullmatch(normalized) is None:
            raise ValueError("phone_number must use E.164 format, for example +989121234567")
        return normalized


class SigninRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("username must not be blank")
        return normalized

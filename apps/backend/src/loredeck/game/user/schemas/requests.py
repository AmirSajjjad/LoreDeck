import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

E164_PHONE_NUMBER = re.compile(r"\+[1-9]\d{7,14}")


def normalized_username(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("username must not be blank")
    return normalized


def normalized_phone_number(value: object) -> object:
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    normalized = value.strip()
    if E164_PHONE_NUMBER.fullmatch(normalized) is None:
        raise ValueError("phone_number must use E.164 format, for example +989121234567")
    return normalized


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
        return normalized_username(value)

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
        return normalized_phone_number(value)


class SigninRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return normalized_username(value)


class UpdateProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str | None = Field(default=None, max_length=255)
    phone_number: str | None = Field(default=None, max_length=16)
    profile_pic: str | None = Field(default=None, max_length=500)
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None

    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, value: object) -> object:
        if value is None:
            raise ValueError("username cannot be null")
        return normalized_username(value) if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, value: object) -> object:
        return normalized_phone_number(value)

    @field_validator("profile_pic", "name", mode="before")
    @classmethod
    def trim_nullable_strings(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def reject_empty_update(self) -> "UpdateProfileRequest":
        if not self.model_fields_set:
            raise ValueError("at least one profile field must be provided")
        return self

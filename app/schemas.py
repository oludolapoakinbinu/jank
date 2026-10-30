from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(pattern=r"^[A-Za-z0-9_]{1,32}$")
    display_name: str = Field(default="", max_length=64)
    bio: str = Field(default="", max_length=160)


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    bio: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=64)
    bio: str | None = Field(default=None, max_length=160)


class FollowCreate(BaseModel):
    follower: str = Field(pattern=r"^[A-Za-z0-9_]{1,32}$")
    following: str = Field(pattern=r"^[A-Za-z0-9_]{1,32}$")


class PostCreate(BaseModel):
    username: str = Field(pattern=r"^[A-Za-z0-9_]{1,32}$")
    body: str = Field(min_length=1, max_length=280)


class LikeCreate(BaseModel):
    username: str = Field(pattern=r"^[A-Za-z0-9_]{1,32}$")


class PostOut(BaseModel):
    id: int
    author: str
    body: str
    like_count: int
    created_at: datetime

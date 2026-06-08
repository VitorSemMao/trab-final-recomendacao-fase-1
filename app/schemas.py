from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    preferences: list[str] = Field(default_factory=list)


class ItemCreate(BaseModel):
    title: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)


class PreferenceUpdate(BaseModel):
    preferences: list[str] = Field(default_factory=list)


class RatingCreate(BaseModel):
    item_id: int = Field(ge=1)
    rating: float = Field(ge=0, le=5)


class UserRead(BaseModel):
    id: int
    name: str
    preferences: list[str]


class ItemRead(BaseModel):
    id: int
    title: str
    tags: list[str]


class RecommendationRead(BaseModel):
    item_id: int
    title: str
    tags: list[str]
    score: float


class RatingRead(BaseModel):
    user_id: int
    item_id: int
    rating: float


class DatasetRead(BaseModel):
    source: str
    items: int
    users: int

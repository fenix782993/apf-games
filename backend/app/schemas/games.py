from pydantic import BaseModel, Field

class ResultIn(BaseModel):
    game: str = Field(min_length=2, max_length=40)
    score: int = Field(ge=0, le=10000000)
    duration: float = Field(default=0, ge=0, le=3600)

class AchievementIn(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    title: str = Field(min_length=2, max_length=160)

from pydantic import BaseModel, ConfigDict, Field


class PublicDeckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    title: str

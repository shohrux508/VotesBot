from pydantic import BaseModel


class CategoryCreate(BaseModel):
    title: str


class CreateCandidate(BaseModel):
    name: str
    category_id: int
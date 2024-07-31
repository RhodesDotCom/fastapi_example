from pydantic import BaseModel, Field
from typing import Optional


class Item(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    description: Optional[str] = None
    price: float

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Sample Item",
                "description": "This is a sample item",
                "price": 10.99
            }
        }
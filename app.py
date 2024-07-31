from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List

from models import Item
from config import settings

app = FastAPI()

# MongoDB 
client = AsyncIOMotorClient(settings.mongodb_url)
database = client[settings.database_name]
collection = database["items"]
counters_collection = database["counters"]


def item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item.get("description"),
        "price": item["price"]
    }


# async def get_next_sequence_value(sequence_name: str) -> int:
#     result = await counters_collection.find_one_and_update(
#         {"_id": sequence_name},
#         {"$inc": {"sequence_value": 1}},
#         return_document=True
#     )
#     if not result:
#         raise HTTPException(status_code=500, detail="Counter document not found.")
#     return result["sequence_value"]


@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    item_dict = item.model_dump(by_alias=True)
    result = await collection.insert_one(item_dict)
    item_dict["_id"] = result.inserted_id
    return item_helper(item_dict)


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_helper(item)

# Get all items
@app.get("/items/", response_model=List[Item])
async def read_items():
    items = []
    async for item in collection.find():
        items.append(item_helper(item))
    return items

# Update an item
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    item_dict = item.model_dump(by_alias=True)
    result = await collection.update_one({"_id": ObjectId(item_id)}, {"$set": item_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    item_dict["_id"] = item_id
    return item_helper(item_dict)

# Delete an item
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
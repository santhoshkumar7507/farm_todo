print("--- Backend server.py starting ---")
from fastapi import FastAPI, HTTPException
from beanie import init_beanie, Document, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import certifi
import uuid
from dotenv import load_dotenv

load_dotenv()

# Models
class ToDoItem(Document):
    content: str
    completed: bool = False
    list_id: PydanticObjectId

class ToDoList(Document):
    name: str

    class Settings:
        name = "todo_lists"

# Response Schemas
class ToDoListSummary(BaseModel):
    id: str
    name: str
    item_count: int

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try to get public IP to help debug whitelisting
    try:
        import urllib.request
        with urllib.request.urlopen('https://api.ipify.org') as response:
            public_ip = response.read().decode('utf-8')
            print(f"Container public IP: {public_ip}")
    except Exception as e:
        print(f"Could not determine public IP: {e}")

    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("MONGODB_URI not found in environment")
        raise ValueError("MONGODB_URI not found in environment")
    
    ca = certifi.where()
    db_connected = False
    try:
        # Extract DB name from URI or use default
        client = AsyncIOMotorClient(
            mongodb_uri, 
            serverSelectionTimeoutMS=5000
        )
        db_name = mongodb_uri.split("/")[-1].split("?")[0] or "todo"
        print(f"Connecting to {db_name}...")
        await init_beanie(database=client[db_name], document_models=[ToDoList, ToDoItem])
        print(f"Connected to MongoDB database: {db_name}")
        db_connected = True
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Running in MOCK mode with in-memory data.")
    
    app.state.db_connected = db_connected
    if not db_connected:
        app.state.mock_lists = []
        app.state.mock_items = []
    
    yield
    # Shutdown logic if needed

app = FastAPI(lifespan=lifespan)

@app.get("/api/lists")
async def get_lists():
    if not app.state.db_connected:
        return [
            {
                "id": l["id"],
                "name": l["name"],
                "item_count": len([i for i in app.state.mock_items if i["list_id"] == l["id"]])
            } for l in app.state.mock_lists
        ]
    try:
        lists = await ToDoList.find_all().to_list()
        summaries = []
        for l in lists:
            count = await ToDoItem.find(ToDoItem.list_id == l.id).count()
            summaries.append({
                "id": str(l.id),
                "name": l.name,
                "item_count": count
            })
        return summaries
    except Exception as e:
        print(f"Error in get_lists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lists")
async def create_list(data: dict):
    if "name" not in data:
        raise HTTPException(status_code=400, detail="Name is required")
    
    if not app.state.db_connected:
        new_id = str(uuid.uuid4())
        new_list = {"id": new_id, "name": data["name"]}
        app.state.mock_lists.append(new_list)
        return {"id": new_id, "name": data["name"], "item_count": 0}

    new_list = ToDoList(name=data["name"])
    await new_list.insert()
    return {"id": str(new_list.id), "name": new_list.name, "item_count": 0}

@app.delete("/api/lists/{list_id}")
async def delete_list(list_id: str):
    if not app.state.db_connected:
        app.state.mock_lists = [l for l in app.state.mock_lists if l["id"] != list_id]
        app.state.mock_items = [i for i in app.state.mock_items if i["list_id"] != list_id]
        return {"message": "Deleted"}

    obj_id = PydanticObjectId(list_id)
    l = await ToDoList.get(obj_id)
    if not l:
        raise HTTPException(status_code=404, detail="List not found")
    await l.delete()
    # Also delete items
    await ToDoItem.find(ToDoItem.list_id == obj_id).delete()
    return {"message": "Deleted"}

@app.get("/api/lists/{list_id}/items")
async def get_items(list_id: str):
    if not app.state.db_connected:
        return [i for i in app.state.mock_items if i["list_id"] == list_id]

    obj_id = PydanticObjectId(list_id)
    items = await ToDoItem.find(ToDoItem.list_id == obj_id).to_list()
    return [{"id": str(i.id), "content": i.content, "completed": i.completed} for i in items]

@app.post("/api/lists/{list_id}/items")
async def add_item(list_id: str, data: dict):
    if "content" not in data:
        raise HTTPException(status_code=400, detail="Content is required")
    
    if not app.state.db_connected:
        new_id = str(uuid.uuid4())
        new_item = {"id": new_id, "content": data["content"], "completed": False, "list_id": list_id}
        app.state.mock_items.append(new_item)
        return new_item

    obj_id = PydanticObjectId(list_id)
    item = ToDoItem(content=data["content"], list_id=obj_id)
    await item.insert()
    return {"id": str(item.id), "content": item.content, "completed": item.completed}

@app.put("/api/items/{item_id}")
async def update_item(item_id: str, data: dict):
    if not app.state.db_connected:
        for i in app.state.mock_items:
            if i["id"] == item_id:
                if "completed" in data: i["completed"] = data["completed"]
                if "content" in data: i["content"] = data["content"]
                return i
        raise HTTPException(status_code=404, detail="Item not found")

    obj_id = PydanticObjectId(item_id)
    item = await ToDoItem.get(obj_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if "completed" in data:
        item.completed = data["completed"]
    if "content" in data:
        item.content = data["content"]
    await item.save()
    return {"id": str(item.id), "content": item.content, "completed": item.completed}

@app.delete("/api/items/{item_id}")
async def delete_item(item_id: str):
    if not app.state.db_connected:
        app.state.mock_items = [i for i in app.state.mock_items if i["id"] != item_id]
        return {"message": "Deleted"}

    obj_id = PydanticObjectId(item_id)
    item = await ToDoItem.get(obj_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await item.delete()
    return {"message": "Deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)

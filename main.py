from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

from models.models import TodoItem

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['todo_app']
collection = db['todos']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/todos/", response_model=TodoItem)
async def create_todo(todo: TodoItem):
    todo_data = todo.model_dump()
    result = collection.insert_one(todo_data)
    todo_data['_id'] = str(result.inserted_id)
    return todo_data


@app.get("/todos/", response_model=list[TodoItem])
async def list_todos():
    todos = list(collection.find())
    return [TodoItem(**todo) for todo in todos]


@app.get("/todos/{todo_id}", response_model=TodoItem)
async def read_todo(todo_id: str):
    todo = collection.find_one({"_id": ObjectId(todo_id)})
    if todo:
        return TodoItem(**todo)
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@app.put("/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: str, todo: TodoItem):
    todo_data = todo.dict(exclude_unset=True)
    result = collection.update_one({"_id": ObjectId(todo_id)}, {"$set": todo_data})
    if result.modified_count == 1:
        updated_todo = collection.find_one({"_id": ObjectId(todo_id)})
        return TodoItem(**updated_todo)
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{todo_id}", response_model=dict)
async def delete_todo(todo_id: str):
    result = collection.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 1:
        return {"message": "Todo deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


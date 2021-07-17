from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict

class Message(BaseModel):
    detail: str

app = FastAPI()

items = {"foo": "The Foo Wrestlers"}


@app.get("/items/{item_id}")   # , responses={404: {"model": Message}, 422: {"model": Message}})
async def read_item(item_id: str) -> Dict[str, str]:
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                            detail="Item not found")
    return {"item": items[item_id]}
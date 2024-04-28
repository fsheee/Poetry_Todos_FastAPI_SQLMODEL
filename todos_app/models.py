from sqlmodel import Field,SQLModel
from typing import  Optional

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)

class TodoResponse(SQLModel): 
    id: int
    content:str
    message:str

class TodoCreate(SQLModel): 
    content:str
    
class TodoUpdate(SQLModel):
    content:str

from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from todos_app import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI,HTTPException, Depends
from .models import Todo, TodoCreate,TodoUpdate,TodoResponse


# class Todo(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     content: str = Field(index=True)

# class TodoResponse(SQLModel): 
#     id: int
#     content:str
# class TodoCreate(SQLModel): 
#     content:str
# class TodoUpdate(SQLModel):
#     content:str
     
  

# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB",
    version="0.0.1"
    # servers=[
        #  {
        # #     "url": "http://127.0.0.1/:8000", # ADD NGROK URL Here Before Creating GPT Action
        #      "description": "Development Server"
        # }
        # ]
)
#dependency injecton
def get_session():
    with Session(engine) as session:
        yield session

#test
@app.get("/")
def read_root():
    return {"message ": "Using FastAPI-SQLMODEL"}

#create todoitem
# @app.post("/todos/", response_model=Todo)
# def create_todo(todo:Todo, session: Annotated[Session, Depends(get_session)]):
        
#         session.add(todo)
#         session.commit()
#         session.refresh(todo)
#         return todo

@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, session: Annotated[Session, Depends(get_session)]):
    
    created_todo = Todo(content=todo.content)
         
    session.add(created_todo)
    session.commit()
    session.refresh(created_todo)
    # return created_todo
    return TodoResponse(id=created_todo.id, content=created_todo.content,
                        message="Todo created successfully")
    

#get all todo
@app.get("/todos/", response_model=list[Todo])
def get_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos

#get single todo by id
@app.get("/todos/{todo_id}",response_model=Todo)
def get_todo_by_id(todo_id:int,session:Annotated[Session,Depends(get_session)]):
  single_id=session.get(Todo,todo_id)
  if not single_id:
    raise HTTPException(status_code=404,detail="Todo ID not found")
  return single_id         


#update
@app.put("/todos/{todo_id}",response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate,session:Annotated[Session,Depends(get_session)]):
    updated_todo = session.exec(select(Todo).where(Todo.id==todo_id)).first()
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo ID not found")
    
    updated_todo.content=todo.content
    session.add(updated_todo)
    session.commit()
    session.refresh(updated_todo)

    # return {"message":"TODO updated Successfully"}
    return TodoResponse(id=updated_todo.id, content=updated_todo.content,
                        message="Todo updated successfully")

#delete

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id:int,session:Annotated[Session,Depends(get_session)]):
  todo_deleted=session.exec(select(Todo).where(Todo.id==todo_id)).first()
  if not todo_deleted:
    raise HTTPException(status_code=404,detail="TODO ID not found")
  session.delete(todo_deleted)
  session.commit()
#   session.refresh(todo_deleted)
  return {"message":"TODO ID Deleted successfully"}
                        

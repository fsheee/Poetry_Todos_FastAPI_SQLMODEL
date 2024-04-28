from fastapi.testclient import TestClient
from sqlmodel import  Session, SQLModel, create_engine
from fastapi import FastAPI
from todos_app.main import app, get_session
from todos_app import settings
import pytest

connection_string: str = str(settings.TEST_DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={
                       "sslmode": "require"}, pool_recycle=300, pool_size=10, echo=True)

#========================================================================================
# Refactor with pytest fixture
# 1- Arrange, 2-Act, 3-Assert 4- Cleanup
#database tables are created before any tests are run
@pytest.fixture(scope="module", autouse=True)
def get_db_session():
    SQLModel.metadata.create_all(engine)
    yield Session(engine)

#  recreated for each test function 
#(test client with the appropriate dependencies overridden for testing )
@pytest.fixture(scope='function')
def test_app(get_db_session):
    def test_session():
        yield get_db_session
    app.dependency_overrides[get_session] = test_session
    with TestClient(app=app) as client:
        yield client

#=========================================================================================

# Test 1: Root test
def test_read_main():
    client = TestClient(app=app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message ": "Using FastAPI-SQLMODEL"}

# Test 2: Create todo
def test_create_todo(test_app):
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:
    #     def get_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
        test_todo = {"content": "created post"}
        response = test_app.post('/todos/', json=test_todo)
        data = response.json()
        assert response.status_code == 200
        assert data["content"] == test_todo["content"]
#testing 3 in wrong
def test_create_todo1(test_app):
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:
    #     def get_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
        test_todo = {"content": "created post"}
        response =test_app.post('/todos/')
        data = response.json()
        assert response.status_code == 200
        assert data["content"]  != test_todo["content"]


#test:4 list of all todos todos list not empty

def test_get_todos(test_app):
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:
    #     def get_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
        # response = client.get('/todos/')
        response = test_app.get('/todos/')
        data = response.json()
        assert response.status_code == 200
        # assert data["content"] ==  
        assert len(data) > 0
# test: 5  get all todos
def test_get_todos1(test_app):
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:
    #     def get_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
        test_todo={"content":"get all todo test list"} # create todo
        response = test_app.post('/todos/',json=test_todo)
        data=response.json()
        #list of todo
        response=test_app.get('/todos/')
        new_todo=response.json()[-1] #created todo in list
        assert response.status_code == 200
        assert new_todo["content"] ==test_todo["content"]
 
 # test 6 get todo by ID
def test_get_todo_by_id(test_app):
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:
    #     def get_session_override(): #test brench override to main in neon
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)    
        test_todo={"content":"get single ID"} 
        response =test_app.post('/todos/',json=test_todo)
        todo_id=response.json()["id"]

        res=test_app.get(f'/todos/{todo_id}')
        data=res.json()
        assert res.status_code==200
        assert data["content"]==test_todo["content"]
        
 # test 7 update todo

def test_update_todo(test_app):
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:
    #     def get_session_override(): #test brench override to main in neon
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
    # Create a todo to update
    test_todo = {"content": "todo to update"}
    response = test_app.post('/todos/', json=test_todo)
    assert response.status_code == 200
    todo_id = response.json()["id"]

    # Update the todo
    updated_todo_data = {"content": "updated content"}
    response = test_app.put(f'/todos/{todo_id}', json=updated_todo_data)
    assert response.status_code == 200

    # Verify the response
    response_data = response.json()
    assert response_data["id"] == todo_id  #    matches updated id
    assert response_data["content"] == "updated content"  #  updated 

# test 8:delete todo        
def test_delete_todo(test_app):    
    # SQLModel.metadata.create_all(engine)  
    # with Session(engine) as session:
    #     def get_session_override(): #test brench override to main in neon
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
        test_todo={"content":"deleted todo test"} 
        response = test_app.post('/todos/',json=test_todo)
        todo_id=response.json()["id"]

        response=test_app.delete(f'/todos/{todo_id}')
        data=response.json()
        assert response.status_code==200
        assert data["message"]=="TODO ID Deleted successfully"


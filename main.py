from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi_neon2.model import Todo, create_db_and_tables , engine, get_session
from sqlmodel import SQLModel, Field, create_engine, Session, select
from contextlib import asynccontextmanager
from typing import Annotated

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Crate table.... ")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=life_span, title="Fast API")

@app.get('/')
def get_root_route():
    return {"Fast API", "App"}

# get todo from database

def get_db_todo():
    with Session(engine) as session:
        get_todos = select(Todo)
        todo_list = session.exec(get_todos).all()
        if not todo_list:
            return "Todo Not Found"
        else:
            return todo_list
        
@app.get('/get_todos', response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
    todo_list = get_db_todo()
    if not todo_list:
        raise HTTPException(status_code=404, detail="Todo Not Found")
    else:
        return todo_list


# insert data into Todo
def create_db_todo(todo : str):
    with Session(engine) as session:
        select_todo = Todo(todo_name=todo)
        session.add(select_todo)
        session.commit()
        session.refresh(select_todo)
        return select_todo
    
@app.post('/add_todo', response_model=Todo) 
def add_todo_route(user_todo :str, session: Annotated[Session,Depends(get_session) ]):
    if not user_todo:
        raise HTTPException(status_code=404, detail="Todo Not Found...")
    else:
        added_todo = create_db_todo(user_todo)
        return added_todo
    
# update todo from database
def update_db_todo(todo_id:int, user_todo:str, session):
    with Session(engine) as session:
        select_todo = select(Todo).where(Todo.id == todo_id)   
        update_todo = session.exec(select_todo).one() 
        update_todo.todo_name = user_todo
        session.add(update_todo)
        session.commit()
        session.refresh(update_todo)
        return update_todo

@app.put('/update_todo/{todo_id}', response_model=Todo)   
def update_todo_name_route(todo_id:int, user_todo: str, session : Annotated[Session, Depends(get_session)]):
    updated_todo_name = update_db_todo(todo_id, user_todo, session )
    return updated_todo_name

def delete_from_table(user_id : int):  
   with Session(engine) as session:
     statment = select(Todo).where(Todo.id == user_id) 
     result = session.exec(statment).first()
     session.delete(result)
     session.commit()
     return result

@app.delete('/delete_todo/{todo_id}/')
def delete_route(todo_id : int, session : Annotated[Session, Depends(get_session)] ):
    delete_todo  = delete_from_table(todo_id) 
    if not delete_todo:
        raise HTTPException(status_code=404, detail='Todo not found' )
    else:
        return {"message" : 'Data Delete Sucessfully ' }






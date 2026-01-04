from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException, Response
from sqlalchemy import create_engine, Column, String, Integer, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import requests


fastapi = FastAPI()


Base = declarative_base()


class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    age = Column(Integer)


engine_people = create_engine("postgresql://postgres:1234@localhost/people")
SessionLocalPeople = sessionmaker(autocommit=False, autoflush=False, bind=engine_people)
session_people = SessionLocalPeople()


Base.metadata.create_all(bind=engine_people)


def get_db_people():
    db = SessionLocalPeople()
    try:
        yield db
    finally:
        db.close()


class AddPerson(BaseModel):
    name:str
    age:int


@fastapi.post('/addperson')
def add_person(person: AddPerson, db: Session = Depends(get_db_people)):
    new_person = Person(name=person.name, age=person.age)
    db.add(new_person)
    db.commit()
    return {"message": "person created successfuly"}


@fastapi.get('/getage/{name}')
def get_age(db: Session = Depends(get_db_people)):
    age = db.query(Person.age).filter(name == Person.name).scalar()
    return {"age": age}


name = input("Enter person's name pls: ")
parameter = name

response = requests.get(name, params=parameter)

print(response.text)


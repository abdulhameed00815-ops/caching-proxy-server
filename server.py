from sqlalchemy import create_engine, Column, String, Integer, LargeBinary, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import requests
from datetime import datetime, timedelta

Base = declarative_base()


class Request(Base):
    __tablename__ = "requests"
    id  = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    type = Column(String)
    response = Column(String, unique=True)
    date = Column(DateTime, default=datetime.datetime.now)


engine_requests = create_engine("postgresql://postgres:1234@localhost/requests")
SessionLocalRequests = sessionmaker(autocommit=False, autoflush=False, bind=engine_requests)
session_requests = SessionLocalRequests()


Base.metadata.create_all(bind=engine_requests)


def get_db_requests():
    db = SessionLocalRequests()
    try:
        yield db
    finally:
        db.close()


def check_input(is_expired: bool):
    url = input("enter request URL: ")
    type = input("enter request type: ")
    if session_requests.query(Request.url).filter(Request.url == url, Request.type == type).scalar() and is_expired is False:
        current_time = datetime.now()
        five_minutes_ago = current_time - timedelta(minutes=5)
        creation_time = session_requests.query(Request.date).filter(Request.url == url).scalar()
        if creation_time < five_minutes:
            is_expired is True
            expired_request = session_requests.query(Request).filter(Request.url == url).first()
            session_requests.delete(expired_request)
            session_requests.commit()
        response = session_requests.query(Request.response).filter(Request.url == url, Request.type == type).scalar()
        print(response)
    else:
        if type == "get":
            response = requests.get(url)
            new_request = Request(url=url, type="get", response=response.text)
            session_requests.add(new_request)
            session_requests.commit()
            print(response.text)


while True:
    choice = input(": ")
    if choice == "help":
        print("""
        enter "request" to make a request
        enter "clear cache" to clear cache
        """)
    elif choice == "request":
        check_input()
    elif choice == "clear cache":
        session_requests.query(Request).delete(synchronize_session=False)
        session_requests.commit()
        print("cache cleared successfuly")
    

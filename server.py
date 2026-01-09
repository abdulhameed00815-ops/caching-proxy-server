from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException, Response
from sqlalchemy import create_engine, Column, String, Integer, LargeBinary, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import requests
from datetime import datetime, timedelta
import httpx #for forwarding requests


Base = declarative_base()


fastapi = FastAPI()


class CachedRequest(Base):
    __tablename__ = "requests"
    id  = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    type = Column(String)
    response = Column(String, unique=True)
    date = Column(DateTime, default=datetime.now)


engine_requests = create_engine("postgresql://postgres:1234@localhost/requests")
SessionLocalRequests = sessionmaker(autocommit=False, autoflush=False, bind=engine_requests)
session_requests = SessionLocalRequests()


Base.metadata.create_all(bind=engine_requests)


class ClientRequest(BaseModel):
    request:str


def get_db_requests():
    db = SessionLocalRequests()
    try:
        yield db
    finally:
        db.close()


def clear_cache():
    session_requests.query(Request).delete(synchronize_session=False)
    session_requests.commit()
    print("cache cleared successfuly")


@fastapi.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(full_path: str, request: Request):
    url = f"http://127.0.0.1:8000/{full_path}" 

    cached_url = session_requests.query(CachedRequest.url).filter(CachedRequest.url == url).scalar()
    if cached_url:
        cached_response = session_requests.query(CachedRequest.response).filter(CachedRequest.url == url).scalar()
        return {"response": cached_response}
    else: 
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=request.headers.raw,
                content=await request.body()    
            )


        new_request = CachedRequest(url=url, type=request.method, response=resp.text)
        session_requests.add(new_request)
        session_requests.commit()
        return {"response": resp.text}

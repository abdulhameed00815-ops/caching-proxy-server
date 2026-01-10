from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException, Response
from sqlalchemy import PrimaryKeyConstraint, create_engine, Column, String, Integer, LargeBinary, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
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
    body = Column(JSONB)
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


# this is a generic route that accepts all kinds of restful requests (proxy), we make a request to it, then the route extracts the path "/{full_path:path}", and that ":path" is just for extracting the 
# "/"s too, then we forward the path to our origin, then all the rest is just caching logic (this is all for get methods), 
@fastapi.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(full_path: str, request: Request):
    url = f"http://127.0.0.1:8000/{full_path}" 

    current_time = datetime.now()
    five_minutes_ago = current_time - timedelta(minutes=5)
    expired_requests = list(session_requests.query(CachedRequest).filter(CachedRequest.date < five_minutes_ago).all())
    for cached_request in expired_requests:
        session_requests.delete(cached_request)
        session_requests.commit()

    if request.method == "GET":
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


            new_request = CachedRequest(url=url, body=None, type=request.method, response=resp.text)
            session_requests.add(new_request)
            session_requests.commit()
            return {"response": resp.text}
    elif request.method == "POST":
        cached_url = session_requests.query(CachedRequest.url).filter(CachedRequest.url == url).scalar()
        cached_body = session_requests.query(CachedRequest.body).filter(CachedRequest.body == await request.json()).scalar()
        if cached_url and cached_body:
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

            body = await request.json()
            new_request = CachedRequest(url=url, body=body, type=request.method, response=resp.text)
            session_requests.add(new_request)
            session_requests.commit()
            return {"response": resp.text}


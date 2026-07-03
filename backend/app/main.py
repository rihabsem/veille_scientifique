from fastapi import FastAPI, HTTPException
from app.model import get_user,insert_user
from app.auth import create_access_token
from app.password import verify_password, hash_password
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from datetime import datetime, timedelta
import re


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="http://localhost:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email : str
    password : str
    update_rate : str

@app.get("/chroma-db")
def test():
    
    return {"message": "Hello World"}

@app.get("/run-coordinateur")
def run_coordinateur():
    try:
        from app.coordinateur import run
        run()
        return {"status": "ok"}
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }

@app.post("/login")
def login(data: LoginRequest):
    user = get_user(data.email)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrecte"
        )
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Mot de passe incorrect"
        )
    # if(data.password != user.hashed_password):
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Mot de passe incorrect"
    #     )
    token = create_access_token({
        "email" : user.email,
        "id" : user.id
    })

    return{
        "access_token":token,
        "token_type":"Bearer"
    }

@app.post("/register")
def register(data: RegisterRequest):
    user = get_user(data.email)
    if user is not None:
        raise HTTPException(
            status_code=400,
            detail="Email déjà utilisé"
        )

    if data.update_rate == "weekly":
        days = 7
    elif data.update_rate == "monthly":
        days = 31
    else:
        raise HTTPException(
            status_code=400,
            detail=f"{data.update_rate}"
        )

    date = datetime.now()
    date_string = re.sub(r"\d{2}:\d{2}:\d{2}\.\d+", "", str(date)).strip()
    date_next = date + timedelta(days=days)
    date_next_string = re.sub(r"\d{2}:\d{2}:\d{2}\.\d+", "", str(date_next)).strip()
    hashed_password = hash_password(data.password)
    insert_user(
        email=data.email,
        hashed_password=hashed_password,
        profil=data.name,
        last_updated_date=date_string,
        next_updated_date=date_next_string,
        weekly_monthly=data.update_rate
    )

    return {"status": "ok"}

    
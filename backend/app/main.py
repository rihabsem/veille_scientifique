from fastapi import FastAPI, HTTPException, Depends
from app.model import get_user,insert_user,get_user_by_id, get_user_profile, get_articles, get_articles_by_date
from app.auth import create_access_token, get_current_user_id
from app.password import verify_password, hash_password
from app.user_query import profile_refinement, launch_LLM
from app.coord import run_batch
from app.data_cleaning import clean_data, get_embedding
from app.vector_db_creation import store_user_in_db, search_articles_for_user
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, Field
from typing import Literal
from datetime import datetime, timedelta
import re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        run_batch,
        trigger=CronTrigger(hour=15, minute=5, timezone='Europe/Brussels'),
        id="daily_coordinateur",
        replace_existing=True
    )
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
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
    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        pattern = r"^[A-Za-z]+\.[A-Za-z]+@ulb\.be$"
        if not re.match(pattern, value):
            raise ValueError(
                "L'adresse email doit appartenir au domaine @ulb.be"
            )
        return value

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email : str
    password : str = Field(min_length=8)
    profile : str = Field(min_length=1)
    update_rate : Literal["weekly", "monthly"]
    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        pattern = r"^[A-Za-z]+\.[A-Za-z]+@ulb\.be$"
        if not re.match(pattern, value):
            raise ValueError(
                "L'adresse email doit appartenir au domaine @ulb.be"
            )
        return value

class SetResultsRequest(BaseModel):
    question1: str = Field(min_length=1)
    question2: str = Field(min_length=1)
    question3: str = Field(min_length=1)

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
    user = insert_user(
        name=data.name,
        email=data.email,
        hashed_password=hashed_password,
        profil=data.profile,
        last_updated_date=date_string,
        next_updated_date=date_next_string,
        weekly_monthly=data.update_rate
    )
    cleaned_data = clean_data(data.profile)
    embedding = get_embedding(cleaned_data)
    store_user_in_db(user, embedding)


    return {"status": "ok"}

@app.get("/questions")
def get_me(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    response_json = profile_refinement(user.profil)
    return response_json

@app.post("/set-results")
def set_results(data: SetResultsRequest, user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    profile = get_user_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profil introuvable")
    answers = [data.question1, data.question2, data.question3]
    print("profile =", profile)
    print("type(profile) =", type(profile))
    print("profile[0] =", profile[0])
    try:
        launch_LLM(profile[0], user_id, answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur LLM: {str(e)}")


@app.get("/dashboard-data")
def get_dashboard_data(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    article_ids = search_articles_for_user(user_id)
    if article_ids is None or len(article_ids) == 0:
        raise HTTPException(status_code=404, detail="Pas encore de résultats disponibles")

    results = get_articles(article_ids, user_id)
    return results


    

    
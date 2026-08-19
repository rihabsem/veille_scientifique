from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from app.model import get_user,insert_user,get_user_by_id, get_user_profile, get_articles, mark_email_sent, update_user_update_rate, update_user_profile, create_reset_token, mark_token_used, verify_reset_token, update_user_password
from app.auth import create_access_token, get_current_user_id
from app.password import verify_password, hash_password
from app.user_query import profile_refinement, launch_LLM
from app.coord import run_batch, first_search
from app.data_cleaning import clean_data, get_embedding
from app.vector_db_creation import store_user_in_db, search_articles_for_user,update_user_embedding
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime, timedelta
import re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from app.email_service import send_email, send_reset_email
from app.database import SessionLocal
from app.search_queue import search_queue
from typing import List
from zoneinfo import ZoneInfo
from apscheduler.triggers.interval import IntervalTrigger
import logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting scheduler...", flush=True)
    scheduler.add_job(
        run_batch,
        trigger=CronTrigger(hour=10, minute=52, timezone=ZoneInfo("Europe/Brussels")),
        id="daily_coordinateur",
        replace_existing=True
    )

    scheduler.start()

    yield

    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://veille-scientifique.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class LoginRequest(BaseModel):
    email: str 
    password: str

class updateRequest(BaseModel):
    profile : str = Field(min_length=1)
    update_rate : Literal["weekly", "monthly"]

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    email : str
    password : str = Field(min_length=8)
    profile : str = Field(min_length=1)
    update_rate : Literal["weekly", "monthly"]
    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(pattern, value):
            raise ValueError(
                "L'adresse email n'est pas valide"
            )
        return value

class QuestionAnswer(BaseModel):
    question: str
    answer: str

class NextQuestionRequest(BaseModel):
    previous: List[QuestionAnswer] = []

class SetResultsRequest(BaseModel):
    answers: List[QuestionAnswer]

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

@app.get("/chroma-db")
def test():
    
    return {"message": "Hello World"}

@app.post("/login")
def login(data: LoginRequest):
    print("Login request received:", data)
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

# --- Étape 1 : première question ---

@app.get("/questions/start")
def start_questions(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    question = profile_refinement(user.profil)
    return {"question": question, "step": 1, "is_last": False}


# --- Étape 2 et 3 : questions suivantes, basées sur l'historique ---

@app.post("/questions/next")
def next_question(data: NextQuestionRequest, user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if len(data.previous) >= 3:
        raise HTTPException(status_code=400, detail="Nombre maximal de questions atteint")

    previous_answers = [
        f"{qa.question}: {qa.answer}" for qa in data.previous
    ]

    question = profile_refinement(user.profil, previous_answers)
    step = len(data.previous) + 1

    return {"question": question, "step": step, "is_last": step == 3}



@app.post("/set-results")
def set_results(data: SetResultsRequest, background_tasks: BackgroundTasks, user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    profile = get_user_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profil introuvable")

    if len(data.answers) != 3:
        raise HTTPException(status_code=400, detail="3 réponses attendues")

    formatted_answers = [
        f"Question: {qa.question}\nAnswer: {qa.answer}" for qa in data.answers
    ]

    try:
        launch_LLM(profile[0], user_id, formatted_answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur LLM: {str(e)}")

    def run_first_search():
        db = SessionLocal()
        try:
            first_search(db, user)
        except Exception as e:
            print(f"Erreur lors de la première recherche pour {user_id}: {e}")
        finally:
            db.close()

    background_tasks.add_task(run_first_search)
    return {"status": "started"}
    


@app.get("/dashboard-data")
def get_dashboard_data(user_id: int = Depends(get_current_user_id)):

    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    article_ids = search_articles_for_user(user.id)
    ids = [id.split("_")[1] for id in article_ids]
    results = get_articles(ids, user.id)

    if not user.email_sent:
        send_email(user.email, results, user.profil)
        mark_email_sent(user.id)

    return results

@app.get("/data")
def get_curent_user(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user

@app.get("/search-status")
def search_status(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    return {
        "status": user.search_status
    }

@app.post("/update")
def update_user_endpoint(data: updateRequest, user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    if user.weekly_monthly != data.update_rate:
        update_user_update_rate(user_id, data.update_rate)
    if user.profil != data.profile:
        update_user_profile(user_id, data.profile)
        profile_cleaned = clean_data(data.profile)
        embedding = get_embedding(profile_cleaned)
        update_user_embedding(user_id, embedding)

    return {"status": "ok"}
    
@app.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    user = get_user(data.email)
    if user is None:
        return {"status": "ok"}
    token = create_reset_token(user.id)
    reset_link = f"https://veille-scientifique.vercel.app/reset-password?token={token}"

    send_reset_email(user.email, reset_link)

    return {"status": "ok"}

@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    user_id = verify_reset_token(data.token)
    if user_id is None:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")

    new_hashed = hash_password(data.new_password)
    update_user_password(user_id, new_hashed)
    mark_token_used(data.token)

    return {"status": "ok"}
from fastapi import FastAPI, HTTPException
from app.model import get_user
from app.auth import create_access_token
from app.password import verify_password
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    # if not verify_password(data.password, user.hashed_password):
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Mot de passe incorrect"
    #     )
    if(data.password != user.hashed_password):
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
    

    
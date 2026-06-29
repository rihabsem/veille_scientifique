from fastapi import FastAPI, HTTPException
from model import get_user

app = FastAPI()

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

@app.get("/api/users/{user_id}")
def get_user(user_id:str):
    id = get_user(user_id)
    if id is not None :
        return id
    raise HTTPException(status_code=404, detail="User not found")
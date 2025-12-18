from config import Config
from fastapi import FastAPI
from app.routers import auth
import uvicorn

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "AI Email Client Backend"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
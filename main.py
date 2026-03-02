from config import Config
from fastapi import FastAPI
from app.routers import auth, database, dify, email, test, user
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(email.router)
app.include_router(user.router)
app.include_router(dify.router)
app.include_router(database.router)
app.include_router(test.router)

@app.get("/")
def read_root():
    return {"message": "AI Email Client Backend"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
import asyncio
import uvicorn
import os
from fastapi import FastAPI
from app.routers import auth, database, dify, email, test, user
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.queue import summary_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(summary_worker())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

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

if __name__ == '__main__':
    port = int(os.environ.get('BACKEND_PORT', 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)
from fastapi import BackgroundTasks, APIRouter, HTTPException

router = APIRouter()

def test_task(name: str):
    print(f"--- TEST TASK STARTED FOR {name} ---", flush=True)

@router.post("/test")
async def test_endpoint(background_tasks: BackgroundTasks):
    print("Pushing test task...")
    background_tasks.add_task(test_task, "User")
    return {"status": "pushed"}
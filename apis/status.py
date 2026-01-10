from fastapi import APIRouter
router = APIRouter(prefix="/status")

@router.get("/")
async def status():
    return {"status": "ok"}
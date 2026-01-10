from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.uploadfile import router as uploadfile_router
from apis.status import router as status_router
from db.database import engine,Base
Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5173"
]

app.router.include_router(uploadfile_router)
app.router.include_router(status_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

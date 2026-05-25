from fastapi import FastAPI
from Controllers.anomalia_controller import router

app = FastAPI()

app.include_router(router)
from fastapi import FastAPI
from api.known_words import router as known_words_router
from api.auth import router as auth_router
from api.voice import router as voice_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(known_words_router)
app.include_router(voice_router)
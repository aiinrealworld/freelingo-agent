from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.voice import router as voice_router
from api.words import router as words_router
from api.progress import router as progress_router

app = FastAPI(title="FreeLingo API", version="1.0.0")



# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Added for Vite/React dev server
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

app.include_router(voice_router)
app.include_router(words_router, prefix="/api")
app.include_router(progress_router, prefix="/api")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "OK", "message": "FreeLingo API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to FreeLingo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
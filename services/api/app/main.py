from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import items, events, placement, mastery
from .database import init_db
from .config import settings

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug
)

# CORS middleware for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/api/v1", tags=["items"])
app.include_router(events.router, prefix="/api/v1", tags=["events"])
app.include_router(placement.router, prefix="/api/v1", tags=["placement"])
app.include_router(mastery.router, prefix="/api/v1", tags=["mastery"])


@app.get("/")
async def root():
    return {
        "message": "MathCoach API",
        "version": settings.api_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}

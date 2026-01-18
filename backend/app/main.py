from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.database import (
    connect_to_mongo, close_mongo_connection,
    get_users_collection, get_refresh_tokens_collection,
    get_words_collection, get_daily_tasks_collection,
    get_tutor_chats_collection
)
from app.settings.get_env import CORS_ORIGINS, APP_ENV
from app.routers import auth, words, tasks, tutor, dashboard
from app.cron.scheduler import start_scheduler, shutdown_scheduler

logger = logging.getLogger(__name__)

async def create_indexes():
    """Create database indexes"""
    try:
        # Users collection
        users_collection = get_users_collection()
        await users_collection.create_index("email", unique=True)
        logger.info("Index created for users.email")
        
        # Refresh tokens collection
        refresh_tokens_collection = get_refresh_tokens_collection()
        await refresh_tokens_collection.create_index("expiresAt", expireAfterSeconds=0)  # TTL index
        await refresh_tokens_collection.create_index("userId")
        await refresh_tokens_collection.create_index("tokenHash")
        logger.info("Indexes created for refresh_tokens")
        
        # Words collection
        words_collection = get_words_collection()
        await words_collection.create_index([("userId", 1), ("normalizedWord", 1)], unique=True)
        await words_collection.create_index([("userId", 1), ("priority", 1), ("state", 1)])
        logger.info("Indexes created for words")
        
        # Daily tasks collection
        daily_tasks_collection = get_daily_tasks_collection()
        await daily_tasks_collection.create_index([("userId", 1), ("date", 1)], unique=True)
        logger.info("Index created for daily_tasks")
        
        # Tutor chats collection
        tutor_chats_collection = get_tutor_chats_collection()
        await tutor_chats_collection.create_index("userId")
        await tutor_chats_collection.create_index("wordId")
        logger.info("Indexes created for tutor_chats")
        
    except Exception as e:
        # Index might already exist, which is fine
        logger.warning(f"Index creation warning (may already exist): {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await create_indexes()
    start_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()
    await close_mongo_connection()

app = FastAPI(
    title="Reverba API",
    description="Backend API for Reverba vocabulary learning application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(words.router)
app.include_router(tasks.router)
app.include_router(tutor.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"message": "Reverba API", "environment": APP_ENV}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

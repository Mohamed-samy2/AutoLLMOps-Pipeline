from fastapi import FastAPI
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from config.config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.DbFactory import DbFactory
from Llm.LlmFactory import LlmFactory
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    postrgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    app.db_engine = create_async_engine(postrgres_conn)
    
    app.session = sessionmaker(
        app.db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    db_factory = DbFactory(config = settings, db_client = app.session)
    
    app.db_client = db_factory.create(
        provider=settings.DB_BACKEND
    )
    
    await app.db_client.connect()


    llm_factory = LlmFactory(settings)

    # llm
    app.llm = llm_factory.create(provider=settings.LLM_PROVIDER)
    app.llm.set_generation_model(model_id=settings.LLM_MODEL_ID)

    conn = await AsyncConnection.connect(conninfo=postrgres_conn.replace("+asyncpg", ""),autocommit=True)
    checkpointer = AsyncPostgresSaver(conn=conn)
    await checkpointer.setup()
    await conn.close()
    
    pool = AsyncConnectionPool(conninfo=postrgres_conn.replace("+asyncpg", ""))
    await pool.open(wait=True)
    app.checkpointer = AsyncPostgresSaver(pool)
    
    yield
    
    print("Shutting down...")
    await app.db_engine.dispose()
    await app.db_client.disconnect()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
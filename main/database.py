from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./DB_hw_26.db"

engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# session = asc_session()

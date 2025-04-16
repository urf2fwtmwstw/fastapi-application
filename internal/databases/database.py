from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from internal.config.config import settings

engine = create_async_engine(url=settings.DATABASE_URL, echo=True)


async def get_db():
    db = async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
    )
    yield db

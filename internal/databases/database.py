from internal.config.config import SQLALCHEMY_DATABASE_URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL, echo=True)


async def get_db():
    db = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield db
from internal.config.config import SQLALCHEMY_DATABASE_URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL, echo=True)

session = async_sessionmaker(bind=engine, expire_on_commit=False)
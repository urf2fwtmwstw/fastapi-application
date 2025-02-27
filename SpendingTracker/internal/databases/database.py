import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

with open("internal/config/config.yaml", "r") as f:
    config = yaml.safe_load(f)


SQLALCHEMY_DATABASE_URL = f"postgresql://{config["database"]["user"]}:{config["database"]["password"]}@{config["database"]["host"]}:{config["database"]["port"]}/{config["database"]["name"]}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
import logging
import yaml
import os
from internal.databases.database import engine, Base, SessionLocal, get_db
from internal.logger import logger
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager

# Load .env file
load_dotenv()

# Load YAML config
with open('internal/config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

class Settings(BaseModel):
    log_level: str = 'INFO'
    app_name: str = 'SpendingTracker'
    database_host: str = 'localhost'
    database_port: int = 5432

settings = Settings(
    log_level=os.environ.get("LOG_LEVEL", "INFO"),
    app_name=os.environ.get("APP_NAME", "Spending Tracker"),
    database_host=config.get("database", {}).get("host", "localhost"),
    database_port=config.get("database", {}).get("port", 5432)
)

logging.basicConfig(level=config.get("log_level", "INFO"))

def validate_config(config):
    if not isinstance(config.get("database", {}).get("host"), str):
        raise ValueError("Database host must be a string")




# OS signals handling
resource = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing resources...")
    validate_config(config)
    resource["msg"] = "Initialized"
    yield
    print("Cleaning up resources...")
    resource.clear()




app = FastAPI(lifespan=lifespan)

#logging requests
@app.middleware('http')
async def log_request_middleware(request: Request, call_next):
    response = await call_next(request)
    logger.info("Request completed",service="Spending Tracker")
    return response



Base.metadata.create_all(bind=engine)




@app.get("/")
async def root():
    logger.info('Root endpoint accessed', service="Spending Tracker")
    return {"message": resource.get("msg", "Resource not initialized")}
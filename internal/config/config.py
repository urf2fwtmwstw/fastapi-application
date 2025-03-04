import yaml, os, logging
from pydantic import BaseModel
from dotenv import load_dotenv

def validate_config(config):
    if not isinstance(config.get("database", {}).get("name"), str):
        raise ValueError("Database name must be a string")



class Settings(BaseModel):
    log_level: str = 'INFO'
    app_name: str = 'SpendingTracker'
    database_host: str = 'localhost'
    database_port: int = 5432


# Load .env file
load_dotenv()

# Load YAML config
def yamlconfig():
    with open('internal/config/config.yaml', 'r') as file:
        conf = yaml.safe_load(file)
        validate_config(conf)
        return conf

config = yamlconfig()

settings = Settings(
    log_level=os.environ.get("LOG_LEVEL", "INFO"),
    app_name=os.environ.get("APP_NAME", "Spending Tracker"),
    database_host=config.get("database", {}).get("host", "localhost"),
    database_port=config.get("database", {}).get("port", 5432)
)


logging.basicConfig(level=config.get("log_level", "INFO"))

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{config["database"]["username"]}:{config["database"]["password"]}@{config["database"]["host"]}/{config["database"]["name"]}"
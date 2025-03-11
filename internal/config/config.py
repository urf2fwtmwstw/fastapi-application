import yaml, logging
from pydantic import BaseModel


def validate_config(config):
    if not isinstance(config.get("database", {}).get("name"), str):
        raise ValueError("Database name must be a string")

# Load YAML config
def yamlconfig():
    with open('internal/config/config.yaml', 'r') as file:
        conf = yaml.safe_load(file)
        validate_config(conf)
        return conf

class Settings(BaseModel):
    log_level: str = "INFO"
    database_host: str = 'localhost'
    database_port: int = 5432

config = yamlconfig()

settings = Settings(
    log_level=config.get("log_level", "INFO"),
    database_host=config.get("database", {}).get("host", "localhost"),
    database_port=config.get("database", {}).get("port", 5432)
)

logging.basicConfig(level=settings.log_level)

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{config["database"]["username"]}:{config["database"]["password"]}@{config["database"]["host"]}/{config["database"]["name"]}"
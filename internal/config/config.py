import yaml
from pydantic import BaseModel


def validate_config(config):
    if not isinstance(config.get("database", {}).get("name"), str):
        raise ValueError("Database name must be a string")

# Load YAML config
def yamlconfig():
    with open('config.yaml', 'r') as file:
        conf = yaml.safe_load(file)
        validate_config(conf)
        return conf

class Database(BaseModel):
    username: str = "postgres"
    password: str = "password"
    host: str = "localhost"
    port: int = 5432
    name: str = "SpendingTrackerDB"

class Logger(BaseModel):
    log_level: str = "INFO"

class Settings(BaseModel):
    logger: Logger
    database: Database

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.database.username}:{self.database.password}@{self.database.host}/{self.database.name}"


settings = Settings(**yamlconfig())
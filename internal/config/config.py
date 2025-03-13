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
    database_username: str = "postgres"
    database_password: str = "password"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "SpendingTrackerDB"

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.database_username}:{self.database_password}@{self.database_host}/{self.database_name}"

config = yamlconfig()

settings = Settings(
    log_level=config.get("log_level"),
    database_username=config.get("database", {}).get("username"),
    database_password=config.get("database", {}).get("password"),
    database_host=config.get("database", {}).get("host"),
    database_port=config.get("database", {}).get("port"),
    database_name=config.get("database", {}).get("name"),
)

logging.basicConfig(level=settings.log_level)
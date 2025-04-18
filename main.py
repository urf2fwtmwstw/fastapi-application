import uvicorn

from app import app
from internal.application.routers import handlers
from internal.logger.log_middleware import LogMiddleware

app.add_middleware(LogMiddleware)
handlers(app)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)

import json
import logging
from datetime import datetime
from logging import Formatter, LogRecord

from internal.config.config import settings


class JsonFormatter(Formatter):
    def __init__(self):
        super(JsonFormatter, self).__init__()

    def format(self, record: LogRecord):
        json_record = {}
        json_record["log_level"] = settings.logger.log_level
        json_record["timestamp"] = str(datetime.now())
        json_record["message"] = record.getMessage()
        if "req" in record.__dict__:
            json_record["request"] = record.__dict__["req"]
        if "res" in record.__dict__:
            json_record["response"] = record.__dict__["res"]
        if record.levelno == logging.ERROR and record.exc_info:
            json_record["error"] = self.formatException(record.exc_info)
        return json.dumps(json_record)


logger = logging.root
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.handlers = [handler]
logger.setLevel(getattr(logging, settings.logger.log_level))

logging.getLogger("uvicorn.access").disabled = True

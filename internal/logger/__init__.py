import logging
import structlog.processors
from structlog import wrap_logger
from structlog.stdlib import add_log_level, add_logger_name


logger = wrap_logger(logging.getLogger(__name__), processors=[
    add_log_level,
    structlog.processors.TimeStamper(fmt='iso'),
    structlog.processors.StackInfoRenderer(),
    structlog.dev.ConsoleRenderer(colors=False)
])


import logging
import structlog
from logging.handlers import RotatingFileHandler
import sys
from structlog import get_logger
from structlog.processors import CallsiteParameter
import logfire
import os
import dotenv

# LOGFILE = "logs/mermaid_agent.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 3


# SET ENVS FIRST
dotenv.load_dotenv(".env")


# logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))


def setup_logging(logfile: str) -> logging.Logger:
    """Configure structlog to log JSON to file and prettified output to stdout."""

    # --- 1. Create handlers ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(fmt="%(message)s"))

    file_handler = logging.FileHandler(logfile)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(fmt="%(message)s"))

    # --- 2. Set up root logger ---
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []  # clear default handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # --- 3. Configure structlog ---
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            # structlog.processors.format_exc_info,
            logfire.StructlogProcessor(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    # --- 4. Attach a processor formatter with different renderers ---
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(),  # pretty for terminal
        foreign_pre_chain=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
        ],
    )

    console_handler.setFormatter(formatter)

    file_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),  # JSON for file
        foreign_pre_chain=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
        ],
    )
    file_handler.setFormatter(file_formatter)

    return get_logger()


logfile_path = "./"  # "/var/ui_server/"
logfile = "ui_server.log"
if not os.path.exists(logfile_path):
    os.mkdir(logfile_path)
logger = setup_logging(os.path.join(logfile_path, logfile))

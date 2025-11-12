import uuid
from dataclasses import dataclass, field
import structlog

from functions_to_format.functions.general.const_values import LanguageOptions


@dataclass
class LoggerContext:
    chat_id: str
    logger: structlog.stdlib.BoundLogger

    def model_dump(self):
        return {
            "chat_id": self.chat_id,
        }


@dataclass
class Context:
    llm_output: str
    backend_output: dict
    version: str
    language: LanguageOptions
    api_key: str
    logger_context: LoggerContext
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def to_json(self):
        return {
            "chat_id": self.logger_context.chat_id,
            "llm_output": self.llm_output,
            "backend_output": self.backend_output,
            "version": self.version,
            "language": self.language.value,
            "api_key": self.api_key,
            "request_id": self.request_id,
        }

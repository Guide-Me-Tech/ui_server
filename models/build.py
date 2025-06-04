from pydantic import BaseModel
from .widget import Widget
from typing import Union, Dict, Any


class BuildOutput(BaseModel):
    widgets_count: int
    widgets: list[Union[Dict[str, Any], Widget]]


class ErrorResponse(BaseModel):
    error: str
    traceback: str

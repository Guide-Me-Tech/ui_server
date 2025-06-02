from pydantic import BaseModel, Field
from typing import Callable, Optional, Dict, Any, Union
import json


class Widget(BaseModel):
    name: str
    type: str
    order: int
    layout: str
    fields: list[str]
    values: Optional[list[Dict]] = None
    ui: Optional[Union[Dict[str, Any], str]] = None

    def build_ui(self, function: Callable, **kwargs):
        self.ui = function(**kwargs)

from pydantic import BaseModel, Field
from typing import Callable, Optional, Dict
import json


class Widget(BaseModel):
    name: str
    type: str
    order: int
    layout: str
    fields: list[str]
    values: Optional[list[Dict]] = None
    ui: Optional[str] = None

    def build_ui(self, function: Callable, **kwargs):
        self.ui = json.dumps(function(**kwargs))

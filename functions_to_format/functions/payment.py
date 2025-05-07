import json
from conf import logger
from .general import (
    add_ui_to_widget,
    Widget,
    TextWidget,
    ButtonsWidget,
    build_text_widget,
    build_buttons_row,
    WidgetInput,
)
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


def get_receiver_id_by_reciver_phone_number(llm_output, backend_output, version="v2"):
    output = []
    backend_output_processed = []
    print(type(backend_output))
    logger.debug(backend_output)
    for i, card_info in enumerate(backend_output):
        print(f"Card {i + 1} info: ", card_info)
        backend_output_processed.append(
            {
                "masked_card_pan": card_info["mask"],
                "card_owner": card_info["name"],
                "provider": card_info["processing"],
            }
        )

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    cards_widget = Widget(
        name="cards_other_list_widget",
        type="cards_other_list_widget",
        order=2,
        layout="vertical",
        fields=["masked_card_pan", "card_owner", "provider"],
        values=backend_output_processed,
    )

    buttons = ButtonsWidget(
        order=3,
        values=[{"text": "cancel"}],
    )

    widgets = add_ui_to_widget(
        {
            get_receiver_id_by_reciver_phone_number_ui: cards_widget,
            build_buttons_row: buttons,
            build_text_widget: text_widget,
        },
        version,
    )

    output = {
        "widgets_count": 3,
        "widgets": [widget.model_dump(exclude_none=True) for widget in widgets],
    }

    return output


def get_receiver_id_by_reciver_phone_number_ui(llm_output, backend_output):
    raise NotImplementedError


# "get_fields_of_supplier": get_fields_of_supplier,
# "get_suppliers_by_category": get_suppliers_by_category,
# "get_categories": get_categories,
#  [
#         {
#             "id": 1,
#             "name": "Мобильные операторы",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056545-57d63349-cdc1-4438-982f-23ae508dd782",
#         },
#     ]
#


class Category(BaseModel):
    id: int
    name: str
    image_url: str


def get_categories(llm_output, backend_output, version="v2"):
    backend_output_processed: List[Category] = []
    for i, category in enumerate(backend_output):
        backend_output_processed.append(
            Category(
                id=category["id"],
                name=category["name"],
                image_url=category["s3Url"],
            )
        )

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    categories_widget = Widget(
        name="payments_list_item_widget",
        type="payments_list_item_widget",
        order=2,
        layout="vertical",
        fields=["id", "name", "image_url"],
        values=[category.model_dump() for category in backend_output_processed],
    )

    buttons = ButtonsWidget(
        order=3,
        values=[
            {"text": "Cancel", "action": "cancel"},
        ],
    )

    widgets = add_ui_to_widget(
        {
            build_get_categories_ui: WidgetInput(
                widget=categories_widget,
                args={"categories": backend_output_processed},
            ),
            build_buttons_row: WidgetInput(
                widget=buttons,
                args={"buttons": [{"text": "Cancel", "action": "cancel"}]},
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    return {
        "widgets_count": 3,
        "widgets": [widget.model_dump(exclude_none=True) for widget in widgets],
    }


def build_get_categories_ui(categories: List[Category]):
    raise NotImplementedError


#  [
#         {
#             "id": 1014,
#             "name": "Crediton.uz",
#             "categoryId": 23,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671093787-252daee5-82ac-4fb4-ba5c-03787fe386f8",
#         },
#     ],
# }


class Supplier(BaseModel):
    id: int
    name: str
    image_url: str


def get_suppliers_by_category(llm_output, backend_output, version="v2"):
    backend_output_processed: List[Supplier] = []
    for i, supplier in enumerate(backend_output):
        backend_output_processed.append(
            Supplier(
                id=supplier["id"],
                name=supplier["name"],
                image_url=supplier["s3Url"],
            )
        )

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    suppliers_widget = Widget(
        name="payments_list_item_widget",
        type="payments_list_item_widget",
        order=2,
        layout="vertical",
        fields=["id", "name", "image_url"],
        values=[supplier.model_dump() for supplier in backend_output_processed],
    )
    buttons_widget = ButtonsWidget(
        order=3,
        values=[
            {"text": "Cancel", "action": "cancel"},
        ],
    )

    widgets = add_ui_to_widget(
        {
            get_suppliers_by_category_ui: WidgetInput(
                widget=suppliers_widget,
                args={"suppliers": backend_output_processed},
            ),
            build_buttons_row: WidgetInput(
                widget=buttons_widget,
                args={"buttons": [{"text": "Cancel", "action": "cancel"}]},
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    return {
        "widgets_count": 3,
        "widgets": [widget.model_dump(exclude_none=True) for widget in widgets],
    }


def get_suppliers_by_category_ui(suppliers: List[Supplier]):
    raise NotImplementedError


# {'code': '0',
#  'description': 'Success',
#  'payload': {'checkUp': True,
#   'checkUpWithResponse': True,
#   'checkUpAfterPayment': False,
#   'fieldList': [{'identName': 'amount',
#     'name': 'Сумма',
#     'order': 2,
#     'type': 'MONEY',
#     'pattern': None,
#     'minValue': 500,
#     'maxValue': 10000000,
#     'fieldSize': 12,
#     'isMain': None,
#     'valueList': []},
#    {'identName': 'paymentNo',
#     'name': 'Номер счёта',
#     'order': 1,
#     'type': 'STRING',
#     'pattern': None,
#     'minValue': None,
#     'maxValue': None,
#     'fieldSize': 15,
#     'isMain': True,
#     'valueList': []}]}}


class Field(BaseModel):
    identName: Optional[str] = None
    name: Optional[str] = None
    order: Optional[int] = None
    type: Optional[str] = None
    pattern: Optional[str] = None
    minValue: Optional[int] = None
    maxValue: Optional[int] = None
    fieldSize: Optional[int] = None
    isMain: Optional[bool] = None
    valueList: List[str] = []


def get_fields_of_supplier(llm_output, backend_output, version="v2"):
    backend_output_processed: List[Field] = []
    for i, field in enumerate(backend_output["fieldList"]):
        backend_output_processed.append(
            Field(
                identName=field["identName"],
                name=field["name"],
                order=field["order"],
                type=field["type"],
                pattern=field["pattern"],
                minValue=field["minValue"],
                maxValue=field["maxValue"],
                fieldSize=field["fieldSize"],
                isMain=field["isMain"],
                valueList=field["valueList"],
            )
        )
    if llm_output:
        text_widget = TextWidget(
            order=1,
            values=[{"text": llm_output}],
        )

    fields_widget = Widget(
        name="fields_widget",
        type="fields_widget",
        order=2,
        layout="vertical",
        fields=[
            "identName",
            "name",
            "order",
            "type",
            "pattern",
            "minValue",
            "maxValue",
            "fieldSize",
            "isMain",
            "valueList",
        ],
        values=[field.model_dump() for field in backend_output_processed],
    )

    button_widget = ButtonsWidget(
        order=3,
        values=[
            {"text": "Cancel", "action": "cancel"},
        ],
    )

    widgets = add_ui_to_widget(
        {
            get_fields_of_supplier_ui: WidgetInput(
                widget=fields_widget,
                args={"fields": backend_output_processed},
            ),
            build_buttons_row: WidgetInput(
                widget=button_widget,
                args={
                    "buttons": [
                        {
                            "text": "Cancel",
                            "action": "cancel",
                        }
                    ]
                },
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    if len(llm_output) > 0:
        return {
            "widgets_count": 3,
            "widgets": [widget.model_dump(exclude_none=True) for widget in widgets],
        }
    else:
        return {
            "widgets_count": 2,
            "widgets": [widget.model_dump(exclude_none=True) for widget in widgets[:2]],
        }


def get_fields_of_supplier_ui(fields: List[Field]):
    raise NotImplementedError

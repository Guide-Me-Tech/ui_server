import json
from conf import logger
from .general import (
    add_ui_to_widget,
    Widget,
    TextWidget,
    ButtonsWidget,
    build_text_widget,
    build_buttons_row,
)


def get_receiver_id_by_reciver_phone_number(llm_output, backend_output, version="v2"):
    output = []
    backend_output_processed = []
    # process backed_output
    #  {
    #     #     "pan": "3b1cdf68-cd9f-496a-b756-cd7884b5b9f9",
    #     #     "name": "A. H",
    #     #     "processing": "uzcard",
    #     #     "mask": "561468******9682"
    #     # },
    print(type(backend_output))
    # if type(backend_output) is str:
    #     backend_output = json.loads(backend_output)
    # for i in backend_output:
    #     print(i)
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
        llm_output,
        backend_output,
    )

    output = {
        "widgets_count": 3,
        "widgets": [widget.model_dump_json() for widget in widgets],
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


def get_categories(llm_output, backend_output, version="v2"):
    backend_output_processed = []
    for i, category in enumerate(backend_output):
        backend_output_processed.append(
            {
                "id": category["id"],
                "name": category["name"],
                "image_url": category["s3Url"],
            }
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
        values=backend_output_processed,
    )

    buttons = ButtonsWidget(
        order=3,
        values=[
            {"text": "Cancel", "action": "cancel"},
        ],
    )

    widgets = add_ui_to_widget(
        {
            build_get_categories_ui: categories_widget,
            build_buttons_row: buttons,
            build_text_widget: text_widget,
        },
        version,
        llm_output,
        backend_output,
    )
    return {
        "widgets_count": 3,
        "widgets": [widget.model_dump_json() for widget in widgets],
    }


def build_get_categories_ui(llm_output, backend_output):
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


def get_suppliers_by_category(llm_output, backend_output, version="v2"):
    backend_output_processed = []
    for i, supplier in enumerate(backend_output):
        backend_output_processed.append(
            {
                "id": supplier["id"],
                "name": supplier["name"],
                "image_url": supplier["s3Url"],
            }
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
        values=backend_output_processed,
    )
    buttons_widget = ButtonsWidget(
        values=[
            {"text": "Cancel", "action": "cancel"},
        ]
    )
    buttons_widget.order = 3
    buttons_widget.fields = ["text", "action"]

    widgets = add_ui_to_widget(
        {
            get_suppliers_by_category_ui: suppliers_widget,
            build_buttons_row: buttons_widget,
            build_text_widget: text_widget,
        },
        version,
        llm_output,
        backend_output,
    )
    return {
        "widgets_count": 3,
        "widgets": [widget.model_dump_json() for widget in widgets],
    }


def get_suppliers_by_category_ui(llm_output, backend_output):
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


def get_fields_of_supplier(llm_output, backend_output, version="v2"):
    backend_output_processed = []
    for i, field in enumerate(backend_output["fieldList"]):
        backend_output_processed.append(
            {
                "identName": field["identName"],
                "name": field["name"],
                "order": field["order"],
                "type": field["type"],
                "pattern": field["pattern"],
                "minValue": field["minValue"],
                "maxValue": field["maxValue"],
                "fieldSize": field["fieldSize"],
                "isMain": field["isMain"],
                "valueList": field["valueList"],
            }
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
        values=backend_output_processed,
    )

    button_widget = ButtonsWidget(
        values=[
            {"text": "Cancel", "action": "cancel"},
        ],
    )

    widgets = add_ui_to_widget(
        {
            get_fields_of_supplier_ui: fields_widget,
            build_buttons_row: button_widget,
            build_text_widget: text_widget,
        },
        version,
        llm_output,
        backend_output,
    )
    if len(llm_output) > 0:
        return {
            "widgets_count": 3,
            "widgets": [widget.model_dump_json() for widget in widgets],
        }
    else:
        return {
            "widgets_count": 2,
            "widgets": [widget.model_dump_json() for widget in widgets[:2]],
        }


def get_fields_of_supplier_ui(llm_output, backend_output):
    raise NotImplementedError

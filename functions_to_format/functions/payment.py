import json
from .general import (
    add_ui_to_widget,
    Widget,
    TextWidget,
    ButtonsWidget,
    build_text_widget,
    build_buttons_row,
    WidgetInput,
)
from .general.utils import save_builder_output
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union, Any
from models.build import BuildOutput
import pydivkit as dv
from tool_call_models.cards import CardsByPhoneNumberResponse, CardInfoByPhoneNumber
from tool_call_models.paynet import (
    CategoriesResponse,
    SupplierByCategoryResponse,
    Supplier,
    Category,
)
from tool_call_models.cards import CardInfoByCardNumberResponse
from conf import logger
from functions_to_format.functions.general.const_values import LanguageOptions
import structlog
from models.context import Context, LoggerContext


def send_money_to_someone_via_card(context: Context) -> BuildOutput:
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    backend_output = {
        "amount": 1000,
        "card_owner_name": "John Doe",
        "marked_card_pan": "*XXXX",
        "processingSystem": "SmartBank",
        "to_card_id": "12345",
    }
    widgets = [
        Widget(
            name="send_money_to_someone_via_card",
            type="send_money_to_someone_via_card",
            order=1,
            layout="vertical",
            fields=[
                "amount",
                "card_owner_name",
                "marked_card_pan",
                "processingSystem",
                "to_card_id",
            ],
            values=[{k: v} for k, v in backend_output.items()],
            ui=backend_output,
        )
    ]
    output = BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def get_number_by_receiver_name(context) -> BuildOutput:
    from models.context import Context

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    logger.info("get_number_by_receiver_name")
    output = []
    # backend_output_processed = []
    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    get_contacts_widget = Widget(
        name="get_contacts_widget",
        type="get_contacts_widget",
        order=2,
        layout="vertical",
        fields=["receiver_name"],
        values=[{"receiver_name": backend_output["receiver_name"]}],
    )

    buttons = ButtonsWidget(
        order=3,
        values=[{"text": "cancel"}],
    )

    names = (
        ",".join(backend_output["receiver_name"])
        if isinstance(backend_output["receiver_name"], list)
        else backend_output["receiver_name"]
    )

    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={
                    "text": f"Contactlaringiz orasidan {names} ismini qidirishimiz kerak. Qidiraylikmi ?"
                },
            ),
            # get_number_by_reciver_number_ui: WidgetInput(
            #     widget=get_contacts_widget,
            #     args={"receiver_name": backend_output["receiver_name"]},
            # ),
            build_buttons_row: WidgetInput(
                widget=buttons,
                args={"button_texts": ["cancel", "search"], "receiver_name": names},
            ),
        },
        version,
    )

    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def get_number_by_reciver_number_ui(receiver_name: Union[str, List[str]]):
    logger.info("get_number_by_reciver_number_ui")
    if isinstance(receiver_name, list):
        search_contact_action = dv.DivAction(
            log_id="search_contact",
            url=f"divkit://search_contact?name={receiver_name}",  # Custom scheme the iOS app will catch
            payload={"name": receiver_name},  # Optional: structured access
        )
    else:
        search_contact_action = dv.DivAction(
            log_id="search_contact",
            url=f"divkit://search_contact?name=[{receiver_name}]",  # Custom scheme the iOS app will catch
            payload={"name": [receiver_name]},  # Optional: structured access
        )

    # Main container
    main_container = dv.DivContainer(
        items=[
            dv.DivContainer(
                items=[],
                action=search_contact_action,
                visibility=dv.DivVisibility.INVISIBLE,
            )
        ]
    )
    div = dv.make_div(main_container)
    with open("logs/json/build_get_number_by_reciver_number_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
        logger.info("Saved to build_get_number_by_reciver_number_ui.json", div=div)
    logger.info("get_number_by_reciver_number_ui done")
    return div


def get_receiver_id_by_receiver_phone_number(context) -> BuildOutput:
    from models.context import Context

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    output = []
    # backend_output_processed = []
    backend_output = CardsByPhoneNumberResponse(**backend_output)

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    get_contacts_widget = Widget(
        name="get_contacts_widget",
        type="get_contacts_widget",
        order=2,
        layout="vertical",
        fields=["receiver_name"],
        values=[x.model_dump() for x in backend_output.cards],
    )

    buttons = ButtonsWidget(
        order=3,
        values=[{"text": "cancel"}],
    )

    widgets = add_ui_to_widget(
        {
            get_receiver_id_by_receiver_phone_number_ui: WidgetInput(
                widget=get_contacts_widget,
                args={"cards": backend_output.cards},
            ),
            build_buttons_row: WidgetInput(
                widget=buttons,
                args={"button_texts": ["cancel"]},
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )

    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def get_receiver_id_by_receiver_phone_number_ui(
    cards: List[CardInfoByPhoneNumber],
) -> Dict[str, Any]:
    """
    Builds a UI similar to the provided image, showing a list of cards for a receiver.
    Expects backend_output to be a dict with a "cards" key containing a list of cards,
    each with fields: "name", "processing", "mask".
    """
    # Example backend_output:
    # {
    #   "cards": [
    #       {"name": "ROMAN GORBUNOV", "processing": "HUMO", "mask": "2269"},
    #       {"name": "ROMAN GORBUNOV", "processing": "HUMO", "mask": "3525"},
    #   ]
    # }
    card_items = []
    for idx, card in enumerate(cards, 1):
        card_items.append(
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=[
                    dv.DivContainer(
                        width=dv.DivFixedSize(value=36),
                        height=dv.DivFixedSize(value=36),
                        background=[dv.DivSolidBackground(color="#F3F6FA")],
                        border=dv.DivBorder(
                            stroke=dv.DivStroke(
                                color="#E5E7EB",
                                width=1,
                            ),
                            corner_radius=18,
                        ),
                        items=[
                            dv.DivContainer(
                                width=dv.DivFixedSize(value=36),
                                height=dv.DivFixedSize(value=36),
                                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                alignment_vertical=dv.DivAlignmentVertical.CENTER,
                                items=[
                                    dv.DivText(
                                        text=str(idx),
                                        font_size=18,
                                        font_weight=dv.DivFontWeight.MEDIUM,
                                        text_color="#3B82F6",
                                        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                        alignment_vertical=dv.DivAlignmentVertical.CENTER,
                                        margins=dv.DivEdgeInsets(
                                            top=7, left=12, right=12, bottom=7
                                        ),
                                    )
                                ],
                            )
                        ],
                        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                        alignment_vertical=dv.DivAlignmentVertical.CENTER,
                        margins=dv.DivEdgeInsets(right=12),
                    ),
                    dv.DivContainer(
                        orientation=dv.DivContainerOrientation.VERTICAL,
                        items=[
                            dv.DivText(
                                text=card.name,
                                font_size=16,
                                font_weight=dv.DivFontWeight.MEDIUM,
                                text_color="#222222",
                                line_height=20,
                            ),
                            dv.DivContainer(
                                orientation=dv.DivContainerOrientation.HORIZONTAL,
                                items=[
                                    dv.DivText(
                                        text=card.processing,
                                        font_size=15,
                                        font_weight=dv.DivFontWeight.BOLD,
                                        text_color="#1976D2",
                                        line_height=18,
                                        letter_spacing=0.2,
                                    ),
                                    dv.DivText(
                                        text="  ••  " + str(card.mask),
                                        font_size=15,
                                        text_color="#374151",
                                        line_height=18,
                                        margins=dv.DivEdgeInsets(left=1),
                                        max_lines=1,
                                        text_alignment_horizontal=dv.DivAlignmentHorizontal.LEFT,
                                    ),
                                ],
                                margins=dv.DivEdgeInsets(top=2),
                                width=dv.DivWrapContentSize(),
                            ),
                        ],
                    ),
                ],
                paddings=dv.DivEdgeInsets(bottom=16, left=16, right=16, top=16),
                background=[dv.DivSolidBackground(color="#FFFFFF")],
                margins=dv.DivEdgeInsets(bottom=0 if idx == len(cards) else 8),
                actions=[
                    dv.DivAction(
                        log_id=f"select_card_{idx}",
                        url=f"divkit://select?card_id={idx}",
                        payload={
                            "card_id": card.pan,
                            "card_name": card.name,
                            "card_processing": card.processing,
                            "card_mask": card.mask,
                        },
                    )
                ],
            )
        )
        # Add divider except after last item
        if idx < len(cards):
            card_items.append(
                dv.DivSeparator(
                    delimiter_style=dv.DivSeparatorDelimiterStyle(
                        color="#F3F6FA",
                    ),
                    width=dv.DivFixedSize(value=1),
                    margins=dv.DivEdgeInsets(left=52, right=0),
                )
            )

    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        items=card_items,
        background=[dv.DivSolidBackground(color="#F9FAFB")],
        border=dv.DivBorder(
            stroke=dv.DivStroke(
                color="#E5E7EB",
                width=1,
            ),
            corner_radius=16,
        ),
        paddings=dv.DivEdgeInsets(bottom=0, left=0, right=0, top=0),
        margins=dv.DivEdgeInsets(bottom=12, left=12, right=12, top=12),
    )

    div = dv.make_div(main_container)
    with open(
        "logs/json/build_get_receiver_id_by_receiver_phone_number_ui.json", "w"
    ) as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def get_categories(context) -> BuildOutput:
    from models.context import Context

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    backend_output = CategoriesResponse(**backend_output)
    backend_output_processed: List[Category] = backend_output.payload

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
                args={"button_texts": ["cancel"]},
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    output = BuildOutput(
        widgets_count=3,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def build_get_categories_ui(categories: List[Category]):
    category_items = []
    for idx, category in enumerate(categories):
        item_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            width=dv.DivFixedSize(value=303),
            # height=dv.DivFixedSize(
            #     value=56
            # ),  # Increased height to allow for vertical centering
            items=[
                dv.DivImage(
                    image_url=category.s3Url,
                    width=dv.DivFixedSize(value=24),
                    height=dv.DivFixedSize(value=24),
                ),
                dv.DivText(
                    text=category.name,
                    font_size=16,
                    font_weight=dv.DivFontWeight.REGULAR,
                    text_color="#000000",
                    margins=dv.DivEdgeInsets(left=14),
                ),
            ],
            alignment_vertical=dv.DivAlignmentVertical.CENTER,  # Added vertical centering
            action=dv.DivAction(
                log_id=f"category_{category.id}_selected",
                payload={"category_id": category.id, "category_name": category.name},
                url=f"divkit://action?type=select_category&id={category.id}&name={category.name}",
            ),
        )
        category_items.append(item_container)

        # Add separator with consistent spacing
        if idx < len(categories) - 1:
            category_items.append(
                dv.DivSeparator(
                    delimiter_style=dv.DivSeparatorDelimiterStyle(color="#E0E0E0"),
                    margins=dv.DivEdgeInsets(top=12, bottom=12),
                )
            )

    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivFixedSize(value=343),
        height=dv.DivFixedSize(value=958),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        items=category_items,
        border=dv.DivBorder(corner_radius=20),
        paddings=dv.DivEdgeInsets(top=16, right=16, bottom=8, left=16),
        margins=dv.DivEdgeInsets(left=16, top=657),
    )

    div = dv.make_div(main_container)
    with open("logs/json/build_get_categories_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def get_suppliers_by_category(context) -> BuildOutput:
    from models.context import Context

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    backend_output = SupplierByCategoryResponse(**backend_output)
    backend_output_processed: List[Supplier] = backend_output.payload

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    suppliers_widget = Widget(
        name="payments_list_item_widget",
        type="payments_list_item_widget",
        order=2,
        layout="vertical",
        fields=["id", "name", "image_url", "category_id"],
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
                args={"button_texts": ["cancel"]},
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    output = BuildOutput(
        widgets_count=3,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def get_suppliers_by_category_ui(suppliers: List[Supplier]):
    supplier_items = []
    for idx, supplier in enumerate(suppliers):
        item_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            width=dv.DivMatchParentSize(),
            height=dv.DivWrapContentSize(),
            alignment_vertical=dv.DivAlignmentVertical.CENTER,
            background=[dv.DivSolidBackground(color="#EBF2FA")],
            paddings=dv.DivEdgeInsets(top=16, bottom=16, left=16, right=16),
            items=[
                dv.DivImage(
                    image_url=supplier.s3Url,
                    width=dv.DivFixedSize(value=32),
                    height=dv.DivFixedSize(value=32),
                    margins=dv.DivEdgeInsets(right=12),
                    scale=dv.DivImageScale.FIT,
                    border=dv.DivBorder(corner_radius=16),
                ),
                dv.DivText(
                    text=supplier.name,
                    font_size=16,
                    font_weight=dv.DivFontWeight.REGULAR,
                    text_color="#000000",
                ),
            ],
            actions=[
                dv.DivAction(
                    log_id=f"supplier_{supplier.id}_selected",
                    payload={
                        "supplier_id": supplier.id,
                        "supplier_name": supplier.name,
                    },
                    url=f"divkit://open_supplier?id={supplier.id}&name={supplier.name}",
                ),
                # dv.DivAction(
                #     log_id=f"supplier_{supplier.id}_selected",
                #     payload={
                #         "supplier_id": supplier.id,
                #         "supplier_name": supplier.name,
                #     },
                #     url=f"divkit://select?id={supplier.id}&name={supplier.name}",
                # ),
            ],
        )
        supplier_items.append(item_container)

        if idx < len(suppliers) - 1:
            supplier_items.append(
                dv.DivSeparator(
                    delimiter_style=dv.DivSeparatorDelimiterStyle(color="#E0E0E0"),
                    margins=dv.DivEdgeInsets(left=60, right=16),
                )
            )

    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(),
        height=dv.DivWrapContentSize(),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        items=supplier_items,
        border=dv.DivBorder(corner_radius=12),
        margins=dv.DivEdgeInsets(top=8, bottom=8, left=8, right=8),
    )

    div = dv.make_div(main_container)
    with open("logs/json/build_get_suppliers_by_category_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


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


def get_fields_of_supplier(context) -> BuildOutput:
    from models.context import Context

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    logger.info("get_fields_of_supplier")
    backend_output_processed: List[Field] = []
    for i, field in enumerate(backend_output["payload"]["fieldList"]):
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
                    "button_texts": [
                        "Cancel",
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
        output = BuildOutput(
            widgets_count=3,
            widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
        )
    else:
        output = BuildOutput(
            widgets_count=2,
            widgets=[widget.model_dump(exclude_none=True) for widget in widgets[:2]],
        )
    save_builder_output(context, output)
    return output


def get_fields_of_supplier_ui(fields: List[Field]):
    logger.info("get_fields_of_supplier_ui", fields=fields)
    return
    raise NotImplementedError()
    div = dv.make_div(
        dv.DivContainer(
            orientation="vertical",
            width=dv.DivFixedSize(value=343),
            height=dv.DivFixedSize(value=555),
            margins=dv.DivEdgeInsets(top=110, left=16),
            items=[
                dv.DivContainer(
                    orientation="vertical",
                    width=dv.DivMatchParentSize(),
                    items=[
                        dv.DivInput(
                            hint_text=str(
                                field.name
                            ),  # Convert to string to ensure not None
                            font_size=16,
                            text_color="#1A1A1A",
                            hint_color="#999999",
                            margins=dv.DivEdgeInsets(bottom=16),
                            keyboard_type="text",  # Ensure text input type
                        )
                        for field in fields
                    ],
                )
            ],
        )
    )
    with open("logs/json/build_get_fields_of_supplier_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


if __name__ == "__main__":
    # check get_contacts with action first
    # output = get_receiver_id_by_receiver_phone_number(
    #     llm_output="", backend_output={"receiver_name": "Aslon"}, version="v3"
    # )
    # with open("logs/json/test_response.json", "w") as f:
    #     json.dump(output.model_dump(), f)
    data = [
        {
            "pan": "kkkkkkxxxxxxyyyyyy",
            "name": "Aslon",
            "processing": "HUMO",
            "mask": "*************1234",
        },
        {
            "pan": "kkkkkkxxxxxxyyasdfafsdfyyyy",
            "name": "Aslon",
            "processing": "HUMO",
            "mask": "*************1235",
        },
        {
            "pan": "kkkkkkxxxxxxyyasdfafsdfyyyy",
            "name": "Aslon",
            "processing": "HUMO",
            "mask": "*************1236",
        },
    ]
    context = Context(
        llm_output="Hello world",
        backend_output=CardsByPhoneNumberResponse.model_validate(data).model_dump(),
        version="v3",
        language=LanguageOptions.UZBEK,
        api_key="test",
        logger_context=LoggerContext(
            chat_id="test",
            logger=logger,
        ),
    )
    output = get_receiver_id_by_receiver_phone_number(context=context)
    with open("logs/json/test_response.json", "w") as f:
        json.dump(output.model_dump(), f, ensure_ascii=False, indent=2)

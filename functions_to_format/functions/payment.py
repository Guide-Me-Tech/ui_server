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
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from models.build import BuildOutput
import pydivkit as dv
from tool_call_models.cards import CardsByPhoneNumberResponse, CardInfoByPhoneNumber
from tool_call_models.paynet import (
    CategoriesResponse,
    SupplierByCategoryResponse,
    SupplierFieldsResponse,
    Supplier,
    Category,
    SuppliersField,
    FieldOptions,
)


def send_money_to_someone_via_card(llm_output: str, backend_output, version="v2"):
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
    return BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )


def get_number_by_receiver_name(
    llm_output, backend_output, version="v2"
) -> BuildOutput:
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

    widgets = add_ui_to_widget(
        {
            get_number_by_reciver_number_ui: WidgetInput(
                widget=get_contacts_widget,
                args={"receiver_name": backend_output["receiver_name"]},
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

    return output


def get_number_by_reciver_number_ui(receiver_name: str):
    search_contact_action = dv.DivAction(
        log_id="search_contact",
        url=f"divkit://search_contact?name={receiver_name}",  # Custom scheme the iOS app will catch
        payload={"name": receiver_name},  # Optional: structured access
    )

    # Main container
    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(),
        height=dv.DivWrapContentSize(),
        background=[dv.DivSolidBackground(color="#ffffff")],
        items=[
            dv.DivText(
                text="Contacts List",
                font_size=24,
                font_weight=dv.DivFontWeight(value="bold"),
                margins=dv.DivEdgeInsets(
                    **{"bottom": 16, "left": 16, "top": 16},
                ),
                actions=[search_contact_action],
            ),
        ],
    )
    return dv.make_div(main_container)


def get_receiver_id_by_receiver_phone_number(
    llm_output, backend_output, version="v2"
) -> BuildOutput:
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

    return output


def get_receiver_id_by_receiver_phone_number_ui(
    cards: List[CardInfoByPhoneNumber],
) -> BuildOutput:
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
                orientation="horizontal",
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
                                alignment_horizontal="center",
                                alignment_vertical="center",
                                items=[
                                    dv.DivText(
                                        text=str(idx),
                                        font_size=18,
                                        font_weight="medium",
                                        text_color="#3B82F6",
                                        alignment_horizontal="center",
                                        alignment_vertical="center",
                                        margins=dv.DivEdgeInsets(
                                            top=7, left=12, right=12, bottom=7
                                        ),
                                    )
                                ],
                            )
                        ],
                        alignment_horizontal="center",
                        alignment_vertical="center",
                        margins=dv.DivEdgeInsets(right=12),
                    ),
                    dv.DivContainer(
                        orientation="vertical",
                        items=[
                            dv.DivText(
                                text=card.name,
                                font_size=16,
                                font_weight="medium",
                                text_color="#222222",
                                line_height=20,
                            ),
                            dv.DivContainer(
                                orientation="horizontal",
                                items=[
                                    dv.DivText(
                                        text=card.processing,
                                        font_size=15,
                                        font_weight="bold",
                                        text_color="#1976D2",
                                        line_height=18,
                                        letter_spacing=0.2,
                                    ),
                                    dv.DivText(
                                        text="  ••  " + str(card.mask),
                                        font_size=15,
                                        text_color="#374151",
                                        line_height=18,
                                        margins=dv.DivEdgeInsets(left=4),
                                    ),
                                ],
                                margins=dv.DivEdgeInsets(top=2),
                            ),
                        ],
                    ),
                ],
                paddings=dv.DivEdgeInsets(bottom=16, left=16, right=16, top=16),
                background=[dv.DivSolidBackground(color="#FFFFFF")],
                margins=dv.DivEdgeInsets(bottom=0 if idx == len(cards) else 8),
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
        orientation="vertical",
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
    with open("get_receiver_id_by_receiver_phone_number_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def get_categories(llm_output, backend_output, version="v2") -> BuildOutput:
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
                args={"button_texts": ["cancel", "submit"]},
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    return BuildOutput(
        widgets_count=3,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )


def build_get_categories_ui(categories: List[Category]):
    category_items = []
    for idx, category in enumerate(categories):
        item_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            width=dv.DivMatchParentSize(),
            height=dv.DivWrapContentSize(),
            alignment_vertical=dv.DivAlignmentVertical.CENTER,
            paddings=dv.DivEdgeInsets(top=12, bottom=12, left=16, right=16),
            items=[
                dv.DivImage(
                    image_url=category.s3Url,
                    width=dv.DivFixedSize(value=24),
                    height=dv.DivFixedSize(value=24),
                    margins=dv.DivEdgeInsets(right=12),
                ),
                dv.DivText(
                    text=category.name,
                    font_size=16,
                    font_weight=dv.DivFontWeight.REGULAR,  # Assuming regular weight
                    text_color="#000000",  # Assuming black color
                ),
            ],
            action=dv.DivAction(
                log_id=f"category_{category.id}_selected",
                payload={"category_id": category.id, "category_name": category.name},
                url=f"divkit://action?type=select_category&id={category.id}&name={category.name}",  # Example action
            ),
        )
        category_items.append(item_container)

        # Add separator, except for the last item
        if idx < len(categories) - 1:
            category_items.append(
                dv.DivSeparator(
                    delimiter_style=dv.DivSeparatorDelimiterStyle(
                        color="#E0E0E0"  # A light gray color for the separator
                    ),
                    margins=dv.DivEdgeInsets(left=16, right=16),  # Indent separator
                )
            )

    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(),
        height=dv.DivWrapContentSize(),
        background=[
            dv.DivSolidBackground(color="#FFFFFF")
        ],  # White background for the list
        items=category_items,
        # Optional: add rounded corners and margins if needed, similar to other UIs
        # border=dv.DivBorder(corner_radius=12),
        # margins=dv.DivEdgeInsets(all=8),
    )

    div = dv.make_div(main_container)
    # For debugging or inspection, you can save the JSON output
    with open("build_get_categories_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def get_suppliers_by_category(llm_output, backend_output, version="v2") -> BuildOutput:
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
                args={"button_texts": ["cancel", "submit"]},
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    return BuildOutput(
        widgets_count=3,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )


def get_suppliers_by_category_ui(suppliers: List[Supplier]):
    supplier_items = []
    for idx, supplier in enumerate(suppliers):
        item_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            width=dv.DivMatchParentSize(),
            height=dv.DivWrapContentSize(),
            alignment_vertical=dv.DivAlignmentVertical.CENTER,
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
            action=dv.DivAction(
                log_id=f"supplier_{supplier.id}_selected",
                payload={"supplier_id": supplier.id, "supplier_name": supplier.name},
                url=f"divkit://action?type=select_supplier&id={supplier.id}&name={supplier.name}",
            ),
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
    with open("get_suppliers_by_category_ui.json", "w") as f:
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


def get_fields_of_supplier(llm_output, backend_output, version="v2") -> BuildOutput:
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
                    "button_texts": [
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
        return BuildOutput(
            widgets_count=3,
            widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
        )
    else:
        return BuildOutput(
            widgets_count=2,
            widgets=[widget.model_dump(exclude_none=True) for widget in widgets[:2]],
        )


def get_fields_of_supplier_ui(fields: List[Field]):
    raise NotImplementedError


if __name__ == "__main__":
    # check get_contacts with action first
    # output = get_receiver_id_by_receiver_phone_number(
    #     llm_output="", backend_output={"receiver_name": "Aslon"}, version="v3"
    # )
    # with open("test_response.json", "w") as f:
    #     json.dump(output.model_dump(), f)
    output = get_receiver_id_by_receiver_phone_number(
        llm_output="Hello world",
        backend_output=CardsByPhoneNumberResponse(
            [
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
        ).model_dump(),
        version="v3",
    )
    with open("test_response.json", "w") as f:
        json.dump(output.model_dump(), f, ensure_ascii=False, indent=2)

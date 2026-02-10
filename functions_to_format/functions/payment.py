import json
from tool_call_models.paynet import (
    PaymentManagerPaymentResponse,
)
from .base_strategy import FunctionStrategy
from .general import (
    Widget,
    ButtonsWidget,
    WidgetInput,
)
from .buttons import build_buttons_row
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pydivkit as dv
from pydivkit.core import Expr
from tool_call_models.paynet import (
    CategoriesResponse,
    SupplierByCategoryResponse,
    Supplier,
    Category,
)
from conf import logger
from functions_to_format.functions.general.const_values import LanguageOptions


# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    text_1,
    caption_1,
    icon,
    avatar,
    divider,
)

# Import smarty_ui blocks for ready-made components
from smarty_ui.blocks import (
    payment_status_widget as smarty_payment_status_widget,
    payment_success_widget,
    payment_failed_widget,
    payment_pending_widget,
    service_list,
    home_balance_widget,
)
from smarty_ui.primitives import smarty_button, smarty_button_filled


class GetCategories(FunctionStrategy):
    """Strategy for payment categories UI."""

    def build_widget_inputs(self, context):
        backend_data = CategoriesResponse(**context.backend_output)
        categories = backend_data.payload
        text_builder, text_input = self.make_text_input(context.llm_output)
        return {
            build_get_categories_ui: WidgetInput(
                widget=Widget(
                    name="payments_list_item_widget",
                    type="payments_list_item_widget",
                    order=2,
                    layout="vertical",
                    fields=["id", "name", "image_url"],
                    values=[c.model_dump() for c in categories],
                ),
                args={"categories": categories},
            ),
            build_buttons_row: WidgetInput(
                widget=ButtonsWidget(
                    order=3, values=[{"text": "Cancel", "action": "cancel"}]
                ),
                args={"button_texts": ["cancel"], "language": context.language},
            ),
            text_builder: text_input,
        }


get_categories = GetCategories()


def build_get_categories_ui(
    categories: List[Category],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build categories UI using smarty_ui service_list component.

    Args:
        categories: List of category objects
        language: Language for localization

    Returns:
        DivKit JSON for the categories UI
    """
    # Get localized title
    titles = {
        LanguageOptions.RUSSIAN: "Категории платежей",
        LanguageOptions.ENGLISH: "Payment Categories",
        LanguageOptions.UZBEK: "To'lov kategoriyalari",
    }
    title = titles.get(language, titles[LanguageOptions.ENGLISH])

    # Convert categories to service_list format
    service_items = []
    for category in categories:
        service_items.append(
            {
                "title": category.name,
                "icon_url": category.s3Url,
                "action_url": f"divkit://action?type=select_category&id={category.id}&name={category.name}",
            }
        )

    # Use smarty_ui service_list component
    categories_widget = service_list(
        title=title,
        items=service_items,
    )

    # Wrap with margins
    container = VStack([categories_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
    with open("logs/json/build_get_categories_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


class GetSuppliersByCategory(FunctionStrategy):
    """Strategy for suppliers list UI."""

    def build_widget_inputs(self, context):
        backend_data = SupplierByCategoryResponse(**context.backend_output)
        suppliers = backend_data.payload
        text_builder, text_input = self.make_text_input(context.llm_output)
        return {
            get_suppliers_by_category_ui: WidgetInput(
                widget=Widget(
                    name="payments_list_item_widget",
                    type="payments_list_item_widget",
                    order=2,
                    layout="vertical",
                    fields=["id", "name", "image_url", "category_id"],
                    values=[s.model_dump() for s in suppliers],
                ),
                args={"suppliers": suppliers},
            ),
            build_buttons_row: WidgetInput(
                widget=ButtonsWidget(
                    order=3, values=[{"text": "Cancel", "action": "cancel"}]
                ),
                args={"button_texts": ["cancel"], "language": context.language},
            ),
            text_builder: text_input,
        }


get_suppliers_by_category = GetSuppliersByCategory()


def get_suppliers_by_category_ui(
    suppliers: List[Supplier],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build suppliers UI using smarty_ui service_list component.

    Args:
        suppliers: List of supplier objects
        language: Language for localization

    Returns:
        DivKit JSON for the suppliers UI
    """
    # Get localized title
    titles = {
        LanguageOptions.RUSSIAN: "Поставщики услуг",
        LanguageOptions.ENGLISH: "Service Providers",
        LanguageOptions.UZBEK: "Xizmat ko'rsatuvchilar",
    }
    title = titles.get(language, titles[LanguageOptions.ENGLISH])

    # Convert suppliers to service_list format
    service_items = []
    for supplier in suppliers:
        service_items.append(
            {
                "title": supplier.name,
                "icon_url": supplier.s3Url,
                "action_url": f"divkit://open_supplier?id={supplier.id}&name={supplier.name}",
            }
        )

    # Use smarty_ui service_list component
    suppliers_widget = service_list(
        title=title,
        items=service_items,
    )

    # Wrap with margins
    container = VStack([suppliers_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
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


class GetFieldsOfSupplier(FunctionStrategy):
    """Strategy for supplier fields UI."""

    def build_widget_inputs(self, context):
        fields_list = []
        for field in context.backend_output["payload"]["fieldList"]:
            fields_list.append(
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
                    valueList=[str(field["valueList"])],
                )
            )

        inp = {}
        if context.llm_output:
            text_builder, text_input = self.make_text_input(context.llm_output)
            inp[text_builder] = text_input

        inp[get_fields_of_supplier_ui] = WidgetInput(
            widget=Widget(
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
                values=[f.model_dump() for f in fields_list],
            ),
            args={"fields": fields_list},
        )
        inp[build_buttons_row] = WidgetInput(
            widget=ButtonsWidget(
                order=3, values=[{"text": "Cancel", "action": "cancel"}]
            ),
            args={"button_texts": ["cancel"], "language": context.language},
        )
        return inp


get_fields_of_supplier = GetFieldsOfSupplier()


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


# Feedback texts for payment actions
PAYMENT_FEEDBACK_TEXTS = {
    LanguageOptions.RUSSIAN: {
        "card_selected": "Карта выбрана",
        "category_selected": "Категория выбрана",
        "supplier_selected": "Поставщик выбран",
        "selection_error": "Ошибка выбора",
    },
    LanguageOptions.ENGLISH: {
        "card_selected": "Card selected",
        "category_selected": "Category selected",
        "supplier_selected": "Supplier selected",
        "selection_error": "Selection error",
    },
    LanguageOptions.UZBEK: {
        "card_selected": "Karta tanlandi",
        "category_selected": "Kategoriya tanlandi",
        "supplier_selected": "Ta'minotchi tanlandi",
        "selection_error": "Tanlash xatosi",
    },
}


def build_pay_for_home_utility_ui(
    payment_response: PaymentManagerPaymentResponse,
    language: LanguageOptions = LanguageOptions.UZBEK,
):
    """Build a payment success card UI using smarty_ui payment_status_widget block component"""

    texts_map = {
        LanguageOptions.UZBEK: {
            "currency": "so'm",
        },
        LanguageOptions.RUSSIAN: {
            "currency": "сум",
        },
        LanguageOptions.ENGLISH: {
            "currency": "USD",
        },
    }

    # Get receiver name from response
    receiver_name = ""
    for item in payment_response.data.response:
        if item.order == 1:
            receiver_name = item.value
            break

    # Get amount and card info
    amount = payment_response.additional.amount if payment_response.additional else "0"
    card_info = f"Карта списания: ·· {payment_response.additional.sender_masked_pan[-4:] if payment_response.additional and payment_response.additional.sender_masked_pan else '****'}"

    # Use smarty_ui payment_status_widget block component
    payment_widget = smarty_payment_status_widget(
        amount=str(amount),
        recipient=receiver_name,
        card_info=card_info,
        status="success",
        currency=texts_map[language]["currency"],
    )

    # Wrap with margins
    container = VStack([payment_widget])
    container.margins = dv.DivEdgeInsets(left=16, top=16, right=16, bottom=16)

    return dv.make_div(container)


class PayForHomeUtility(FunctionStrategy):
    """Strategy for home utility payment UI with fallback."""

    def build_widget_inputs(self, context):
        backend_data = PaymentManagerPaymentResponse.model_validate(
            context.backend_output
        )
        text_builder, text_input = self.make_text_input(context.llm_output)
        return {
            text_builder: text_input,
            build_pay_for_home_utility_ui: WidgetInput(
                widget=Widget(
                    order=2,
                    type="payment_status_widget",
                    name="payment_status_widget",
                    layout="vertical",
                    fields=["payment_status"],
                    values=[backend_data.model_dump()],
                ),
                args={"payment_response": backend_data},
            ),
        }

    def execute(self, context):
        try:
            return super().execute(context)
        except Exception:
            text_builder, text_input = self.make_text_input(context.llm_output)
            return self._build_and_save(context, {text_builder: text_input})


pay_for_home_utility = PayForHomeUtility()


# ============================================================================
# Payment Status UI using smarty_ui
# ============================================================================


def build_payment_success_ui(
    amount: str,
    recipient: str,
    card_last_digits: str,
    icon_url: str | None = None,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build payment success UI using smarty_ui payment_success_widget.

    Args:
        amount: Payment amount
        recipient: Recipient/service name
        card_last_digits: Last 4 digits of the card
        icon_url: Optional merchant/service icon URL
        language: Language for localization

    Returns:
        DivKit JSON for the payment success UI
    """
    texts_map = {
        LanguageOptions.UZBEK: {"currency": "so'm", "card_info": "Yechilgan karta"},
        LanguageOptions.RUSSIAN: {"currency": "сум", "card_info": "Карта списания"},
        LanguageOptions.ENGLISH: {"currency": "UZS", "card_info": "Card used"},
    }
    texts = texts_map.get(language, texts_map[LanguageOptions.ENGLISH])
    card_info = f"{texts['card_info']}: ·· {card_last_digits}"

    # Use smarty_ui payment_success_widget
    success_widget = payment_success_widget(
        amount=amount,
        recipient=recipient,
        card_info=card_info,
        icon_url=icon_url,
        currency=texts["currency"],
    )

    # Wrap with margins
    container = VStack([success_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
    with open("logs/json/build_payment_success_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def build_payment_failed_ui(
    amount: str,
    recipient: str,
    card_last_digits: str,
    icon_url: str | None = None,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build payment failed UI using smarty_ui payment_failed_widget.

    Args:
        amount: Payment amount
        recipient: Recipient/service name
        card_last_digits: Last 4 digits of the card
        icon_url: Optional merchant/service icon URL
        language: Language for localization

    Returns:
        DivKit JSON for the payment failed UI
    """
    texts_map = {
        LanguageOptions.UZBEK: {"currency": "so'm", "card_info": "Yechilgan karta"},
        LanguageOptions.RUSSIAN: {"currency": "сум", "card_info": "Карта списания"},
        LanguageOptions.ENGLISH: {"currency": "UZS", "card_info": "Card used"},
    }
    texts = texts_map.get(language, texts_map[LanguageOptions.ENGLISH])
    card_info = f"{texts['card_info']}: ·· {card_last_digits}"

    # Use smarty_ui payment_failed_widget
    failed_widget = payment_failed_widget(
        amount=amount,
        recipient=recipient,
        card_info=card_info,
        icon_url=icon_url,
        currency=texts["currency"],
    )

    # Wrap with margins
    container = VStack([failed_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
    with open("logs/json/build_payment_failed_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def build_payment_pending_ui(
    amount: str,
    recipient: str,
    card_last_digits: str,
    icon_url: str | None = None,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build payment pending UI using smarty_ui payment_pending_widget.

    Args:
        amount: Payment amount
        recipient: Recipient/service name
        card_last_digits: Last 4 digits of the card
        icon_url: Optional merchant/service icon URL
        language: Language for localization

    Returns:
        DivKit JSON for the payment pending UI
    """
    texts_map = {
        LanguageOptions.UZBEK: {"currency": "so'm", "card_info": "Yechilgan karta"},
        LanguageOptions.RUSSIAN: {"currency": "сум", "card_info": "Карта списания"},
        LanguageOptions.ENGLISH: {"currency": "UZS", "card_info": "Card used"},
    }
    texts = texts_map.get(language, texts_map[LanguageOptions.ENGLISH])
    card_info = f"{texts['card_info']}: ·· {card_last_digits}"

    # Use smarty_ui payment_pending_widget
    pending_widget = payment_pending_widget(
        amount=amount,
        recipient=recipient,
        card_info=card_info,
        icon_url=icon_url,
        currency=texts["currency"],
    )

    # Wrap with margins
    container = VStack([pending_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
    with open("logs/json/build_payment_pending_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


# ============================================================================
# Home Balance Widget UI using smarty_ui
# ============================================================================


def build_home_balance_widget_ui(
    title: str,
    subtitle: str,
    utilities: List[Dict[str, Any]],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build home balance widget UI using smarty_ui home_balance_widget component.

    Args:
        title: Widget title (e.g., address)
        subtitle: Widget subtitle (e.g., "Балансы")
        utilities: List of utility balance data dicts with keys:
            - utility_type: "electricity", "gas", "water", "recycling", or "other"
            - balance: Formatted balance string
            - currency: Currency suffix
            - is_negative: Whether balance is negative
            - action_url: Optional tap action URL
        language: Language for localization

    Returns:
        DivKit JSON for the home balance widget UI
    """
    # Use smarty_ui home_balance_widget component
    home_widget = home_balance_widget(
        title=title,
        subtitle=subtitle,
        utilities=utilities,
    )

    # Wrap with margins
    container = VStack([home_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
    with open("logs/json/build_home_balance_widget_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


# Import at top level would cause circular import, so keep as function
def get_home_utility_suppliers(context):
    from .balance import get_home_balances

    return get_home_balances(context)

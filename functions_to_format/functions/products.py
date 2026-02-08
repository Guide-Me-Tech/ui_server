import os
import sys

sys.path.append("/home/aslonhamidov/Desktop/work/ui_server")
from functions_to_format.functions.general.const_values import LanguageOptions
import pydivkit as dv
from pydivkit.core import Expr
from datetime import timedelta
import json, sys
from pydantic import BaseModel
from typing import List, Optional
from functions_to_format.functions.general import (
    Widget,
    WidgetInput,
    create_feedback_variables,
    create_success_actions,
    create_failure_actions,
    create_success_container,
    create_error_container,
    get_feedback_text,
)
from conf import logger
from tool_call_models.smartbazar import SearchProductsResponse, ProductItem
import structlog
from models.context import Context
from .base_strategy import FunctionStrategy

# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    title_2,
    text_1,
    text_2,
    caption_1,
    caption_2,
    icon,
    default_theme,
)

# -------------------------------------------------------------------
#  Функция-шаблон: возвращает dv.DivState с двумя состояниями — collapsed
#  и expanded. Переключение реализовано через dv.DivAction -> SetState.
# -------------------------------------------------------------------
# import pydivkit as dv
# import json


class GetProducts(FunctionStrategy):
    """Strategy for building products list UI."""

    def build_widget_inputs(self, context):
        backend_output_model = SearchProductsResponse(**context.backend_output)
        products = backend_output_model.products
        context.logger_context.logger.info("Products", products=products)

        text_builder, text_input = self.make_text_input(context.llm_output)
        return {
            build_products_list_widget: WidgetInput(
                widget=Widget(
                    name="products_list_widget",
                    type="products_list_widget",
                    order=1,
                    layout="vertical",
                    fields=["products", "title"],
                ),
                args={
                    "products_list_input": products,
                    "language": context.language,
                    "chat_id": context.logger_context.chat_id,
                    "api_key": context.api_key,
                },
            ),
            text_builder: text_input,
        }


get_products = GetProducts()
search_products = get_products


def make_product_state(
    p: ProductItem,
    index: int,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
    chat_id: str = "BLABLABLA",
    api_key: str = "BLABLABLA",
):
    """Create a product state element using pydivkit SDK classes"""
    product_state_id = f"product_{p.id}_{index}"  # Make unique by adding index
    cart_container = f"cart_container_{p.id}_{index}_2"
    feedback_prefix = f"product_{p.id}_{index}"

    texts_map = {
        LanguageOptions.ENGLISH: {
            "price": "Price: {price}",
            "summ": "summ",
            "months": "months",
            "more": "More",
            "hide": "Hide",
            "add": "Add to cart",
            "added_to_cart": "Added to cart!",
            "cart_error": "Failed to add to cart",
        },
        LanguageOptions.UZBEK: {
            "price": "Narxi: {price}",
            "summ": "so'm",
            "months": "oy",
            "more": "Ko'proq",
            "hide": "Yopish",
            "add": "Savatga qo'shish",
            "added_to_cart": "Savatga qo'shildi!",
            "cart_error": "Savatga qo'shib bo'lmadi",
        },
        LanguageOptions.RUSSIAN: {
            "price": "Цена: {price}",
            "summ": "сум",
            "months": "мес",
            "more": "Подробнее",
            "hide": "Скрыть",
            "add": "Добавить в корзину",
            "added_to_cart": "Добавлено в корзину!",
            "cart_error": "Не удалось добавить в корзину",
        },
    }

    # Safely get image URLs
    main_image_mobile_url = ""
    main_image_desktop_url = ""
    if isinstance(p.images, dict):
        mobile_images = p.images.get("mobile", [])
        if mobile_images and isinstance(mobile_images, list):
            main_image_mobile_url = mobile_images[0]
        else:
            main_image_mobile_url = ""
        desktop_images = p.images.get("desktop", [])
        if desktop_images and isinstance(desktop_images, list):
            main_image_desktop_url = desktop_images[0]
        else:
            main_image_desktop_url = ""

    if not main_image_mobile_url and main_image_desktop_url:
        main_image_mobile_url = main_image_desktop_url
    elif not main_image_desktop_url and main_image_mobile_url:
        main_image_desktop_url = main_image_mobile_url

    # Get price information from the new Price schema
    price_text = ""
    if p.price and p.price.price:
        price_text = f"{p.price.price} {texts_map[language]['summ']}"

    # Determine installment pricing for the expanded view
    installment_price_text = price_text
    # if p.price and p.price.installments:
    #     # Find 12-month installment if available
    #     twelve_month_installment = None
    #     for installment in p.price.installments:
    #         if installment.period == 12:
    #             twelve_month_installment = installment
    #             break

    #     if twelve_month_installment and twelve_month_installment.price:
    #         installment_price_text = f"{twelve_month_installment.price} {texts_map[language]['summ']} x 12 {texts_map[language]['months']}"
    # elif p.price and p.price.monthly:
    #     installment_price_text = f"{p.price.monthly} {texts_map[language]['summ']} x 12 {texts_map[language]['months']}"          # TODO: uncomment this when installment service is back again.

    # Collapsed state div using smarty_ui
    product_image = dv.DivImage(
        image_url=main_image_mobile_url,
        width=dv.DivFixedSize(value=40),
        height=dv.DivFixedSize(value=40),
        scale=dv.DivImageScale.FILL,
    )

    product_name = text_1(p.name, color="#111133")
    product_name.font_weight = dv.DivFontWeight.MEDIUM

    product_price = caption_1(price_text, color="#6B7280")

    product_info = VStack([product_name, product_price])
    product_info.width = dv.DivWrapContentSize()

    collapsed_div = HStack(
        [product_image, product_info],
        padding=12,
        background="#FFFFFF",
        corner_radius=8,
    )
    collapsed_div.margins = dv.DivEdgeInsets(bottom=8)
    collapsed_div.border = dv.DivBorder(
        corner_radius=8, stroke=dv.DivStroke(color="#E5E7EB")
    )
    collapsed_div.actions = [
        dv.DivAction(
            log_id=f"expand_product_{p.id}_{index}",
            url=f"sample-actions://set_state?state_id=0/{product_state_id}/expanded",
        ),
        dv.DivAction(
            log_id=f"expand_product_{p.id}_{index}_div",
            url=f"div-action://set_state?state_id=0/{product_state_id}/expanded",
        ),
    ]

    # Success feedback container for cart actions using smarty_ui
    success_icon = caption_1("✅")
    success_icon.margins = dv.DivEdgeInsets(right=8)

    success_text = caption_1(texts_map[language]["added_to_cart"], color="#065F46")
    success_text.font_weight = dv.DivFontWeight.MEDIUM
    success_text.width = dv.DivMatchParentSize(weight=1)

    dismiss_success = caption_1("✕", color="#065F46")
    dismiss_success.font_size = 16
    dismiss_success.font_weight = dv.DivFontWeight.BOLD
    dismiss_success.paddings = dv.DivEdgeInsets(left=8, right=4)
    dismiss_success.actions = [
        dv.DivAction(
            log_id=f"dismiss-success-{feedback_prefix}",
            url=f"div-action://set_variable?name={feedback_prefix}_success_visible&value=0",
        )
    ]

    success_container = HStack(
        [success_icon, success_text, dismiss_success],
        padding=10,
        background="#ECFDF5",
        corner_radius=8,
        width=dv.DivMatchParentSize(),
    )
    success_container.id = f"success-{feedback_prefix}"
    success_container.visibility = Expr(
        f"@{{{feedback_prefix}_success_visible == 1 ? 'visible' : 'gone'}}"
    )
    success_container.margins = dv.DivEdgeInsets(top=8, bottom=8)
    success_container.border = dv.DivBorder(
        corner_radius=8, stroke=dv.DivStroke(color="#A7F3D0", width=1)
    )

    # Error feedback container for cart actions using smarty_ui
    error_icon = caption_1("⚠️")
    error_icon.margins = dv.DivEdgeInsets(right=8)

    error_text = caption_1(texts_map[language]["cart_error"], color="#B91C1C")
    error_text.font_weight = dv.DivFontWeight.MEDIUM
    error_text.width = dv.DivMatchParentSize(weight=1)

    dismiss_error = caption_1("✕", color="#B91C1C")
    dismiss_error.font_size = 16
    dismiss_error.font_weight = dv.DivFontWeight.BOLD
    dismiss_error.paddings = dv.DivEdgeInsets(left=8, right=4)
    dismiss_error.actions = [
        dv.DivAction(
            log_id=f"dismiss-error-{feedback_prefix}",
            url=f"div-action://set_variable?name={feedback_prefix}_error_visible&value=0",
        )
    ]

    error_container = HStack(
        [error_icon, error_text, dismiss_error],
        padding=10,
        background="#FEF2F2",
        corner_radius=8,
        width=dv.DivMatchParentSize(),
    )
    error_container.id = f"error-{feedback_prefix}"
    error_container.visibility = Expr(
        f"@{{{feedback_prefix}_error_visible == 1 ? 'visible' : 'gone'}}"
    )
    error_container.margins = dv.DivEdgeInsets(top=8, bottom=8)
    error_container.border = dv.DivBorder(
        corner_radius=8, stroke=dv.DivStroke(color="#FECACA", width=1)
    )

    # Create on_success actions for cart add
    cart_success_actions = [
        dv.DivAction(
            log_id=f"cart-success-show-{feedback_prefix}",
            url=f"div-action://set_variable?name={feedback_prefix}_success_visible&value=1",
        ),
        dv.DivAction(
            log_id=f"cart-hide-error-{feedback_prefix}",
            url=f"div-action://set_variable?name={feedback_prefix}_error_visible&value=0",
        ),
    ]

    # Create on_fail actions for cart add
    cart_fail_actions = [
        dv.DivAction(
            log_id=f"cart-error-show-{feedback_prefix}",
            url=f"div-action://set_variable?name={feedback_prefix}_error_visible&value=1",
        ),
        dv.DivAction(
            log_id=f"cart-hide-success-{feedback_prefix}",
            url=f"div-action://set_variable?name={feedback_prefix}_success_visible&value=0",
        ),
    ]

    # Expanded state header row using smarty_ui
    exp_product_image = dv.DivImage(
        image_url=main_image_mobile_url,
        width=dv.DivFixedSize(value=40),
        height=dv.DivFixedSize(value=40),
        scale=dv.DivImageScale.FILL,
    )

    exp_product_name = text_1(p.name, color="#111133")
    exp_product_name.font_weight = dv.DivFontWeight.MEDIUM

    exp_product_price = caption_1(price_text, color="#6B7280")

    exp_product_info = VStack([exp_product_name, exp_product_price])
    exp_product_info.width = dv.DivWrapContentSize()

    exp_header_row = HStack([exp_product_image, exp_product_info])
    exp_header_row.actions = [
        dv.DivAction(
            log_id=f"collapse_product_{p.id}_{index}",
            url=f"sample-actions://set_state?state_id=0/{product_state_id}/collapsed",
        ),
        dv.DivAction(
            log_id=f"collapse_product_{p.id}_{index}_div",
            url=f"div-action://set_state?state_id=0/{product_state_id}/collapsed",
        ),
    ]

    # Main product image
    main_product_image = dv.DivImage(
        image_url=main_image_mobile_url,
        width=dv.DivMatchParentSize(),
        height=dv.DivWrapContentSize(),
        margins=dv.DivEdgeInsets(top=12),
        scale=dv.DivImageScale.FIT,
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        alignment_vertical=dv.DivAlignmentVertical.CENTER,
    )

    # Product details using smarty_ui
    detail_name = caption_1(p.name, color="#374151")
    detail_name.margins = dv.DivEdgeInsets(top=8)

    rating_text = caption_2(f"⭐ {p.rate or 0}", color="#6B7280")
    rating_text.margins = dv.DivEdgeInsets(top=4)

    installment_label = caption_2(installment_price_text, color="#DB2777")
    installment_label.background = [dv.DivSolidBackground(color="#FCE7F3")]
    installment_label.paddings = dv.DivEdgeInsets(left=6, top=4, right=6, bottom=4)
    installment_label.margins = dv.DivEdgeInsets(top=6)
    installment_label.border = dv.DivBorder(
        corner_radius=4, stroke=dv.DivStroke(color="#FCE7F3")
    )

    # Build buttons using smarty_ui text components
    hide_btn = text_1(texts_map[language]["hide"], color="#6B7280")
    hide_btn.border = dv.DivBorder(
        corner_radius=8, stroke=dv.DivStroke(color="#D1D5DB")
    )
    hide_btn.height = dv.DivFixedSize(value=36)
    hide_btn.width = dv.DivMatchParentSize()
    hide_btn.alignment_horizontal = dv.DivAlignmentHorizontal.CENTER
    hide_btn.alignment_vertical = dv.DivAlignmentVertical.CENTER
    hide_btn.text_alignment_horizontal = dv.DivAlignmentHorizontal.CENTER
    hide_btn.text_alignment_vertical = dv.DivAlignmentVertical.CENTER
    hide_btn.paddings = dv.DivEdgeInsets(left=16, right=16)
    hide_btn.margins = dv.DivEdgeInsets(left=4) if p.offer_id else dv.DivEdgeInsets()
    hide_btn.actions = [
        dv.DivAction(
            log_id=f"collapse_from_button_{p.id}_{index}",
            url=f"sample-actions://set_state?state_id=0/{product_state_id}/collapsed",
        ),
        dv.DivAction(
            log_id=f"collapse_from_button_{p.id}_{index}_div",
            url=f"div-action://set_state?state_id=0/{product_state_id}/collapsed",
        ),
    ]

    if p.offer_id:
        add_btn = text_1(texts_map[language]["add"], color="#2563EB")
        add_btn.border = dv.DivBorder(
            corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
        )
        add_btn.height = dv.DivFixedSize(value=36)
        add_btn.width = dv.DivMatchParentSize()
        add_btn.alignment_horizontal = dv.DivAlignmentHorizontal.CENTER
        add_btn.alignment_vertical = dv.DivAlignmentVertical.CENTER
        add_btn.text_alignment_horizontal = dv.DivAlignmentHorizontal.CENTER
        add_btn.text_alignment_vertical = dv.DivAlignmentVertical.CENTER
        add_btn.paddings = dv.DivEdgeInsets(left=16, right=16)
        add_btn.margins = dv.DivEdgeInsets(right=4)
        add_btn.actions = [
            dv.DivAction(
                url="divkit://send-request",
                log_id=f"add_to_cart_{p.id}_{index}",
                typed=dv.DivActionSubmit(
                    container_id=cart_container,
                    request=dv.DivActionSubmitRequest(
                        url=f"https://smarty.smartbank.uz/chat/v3/tools/call?function_name=add_product_to_cart&chat_id={chat_id}&arguments={json.dumps({'offer_id': p.offer_id, 'quantity': 1})}",
                        method=dv.RequestMethod.POST,
                        headers=[dv.RequestHeader(name="api-key", value=api_key)],
                    ),
                    on_success_actions=cart_success_actions,
                    on_fail_actions=cart_fail_actions,
                ),
                payload={
                    "function_name": "add_product_to_cart",
                    "chat_id": chat_id,
                    "arguments": {
                        "offer_id": p.offer_id,
                        "quantity": 1,
                    },
                },
            ),
        ]
        buttons_items = [add_btn, hide_btn]
    else:
        hide_btn.margins = dv.DivEdgeInsets()
        buttons_items = [hide_btn]

    # Buttons container using HStack
    buttons_row = HStack(buttons_items, width=dv.DivMatchParentSize())
    buttons_row.margins = dv.DivEdgeInsets(top=12)
    buttons_row.id = cart_container
    buttons_row.content_alignment_horizontal = (
        dv.DivContentAlignmentHorizontal.SPACE_BETWEEN
        if p.offer_id
        else dv.DivContentAlignmentHorizontal.CENTER
    )
    buttons_row.alignment_horizontal = dv.DivAlignmentHorizontal.CENTER

    # Expanded state div using VStack
    expanded_div = VStack(
        [
            exp_header_row,
            main_product_image,
            detail_name,
            rating_text,
            installment_label,
            # Feedback containers
            success_container,
            error_container,
            buttons_row,
        ],
        padding=12,
        background="#FFFFFF",
        corner_radius=12,
    )
    expanded_div.margins = dv.DivEdgeInsets(bottom=8)
    expanded_div.border = dv.DivBorder(
        corner_radius=12, stroke=dv.DivStroke(color="#E5E7EB")
    )
    expanded_div.variables = [
        dv.IntegerVariable(name=f"{feedback_prefix}_success_visible", value=0),
        dv.IntegerVariable(name=f"{feedback_prefix}_error_visible", value=0),
    ]

    return dv.DivState(
        id=product_state_id,
        default_state_id="collapsed",
        states=[
            dv.DivStateState(state_id="collapsed", div=collapsed_div),
            dv.DivStateState(state_id="expanded", div=expanded_div),
        ],
    )


def build_products_list_widget(
    products_list_input: List[ProductItem],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
    chat_id: str = "BLABLABLA",
    api_key: str = "BLABLABLA",
):
    """Build products list widget using smarty_ui components."""
    logger = structlog.get_logger()
    logger.info(
        "Starting build_products_list_widget",
        products_count=len(products_list_input) if products_list_input else 0,
        language=language.value,
        chat_id=chat_id,
    )

    card_log_id = "products_list_card"

    texts_map = {
        LanguageOptions.ENGLISH: {
            "no_products": "No products to display.",
        },
        LanguageOptions.UZBEK: {
            "no_products": "Mahsulotlar yo'q.",
        },
        LanguageOptions.RUSSIAN: {
            "no_products": "Товаров нет.",
        },
    }

    if not products_list_input:
        logger.warning("No products provided, returning empty state")
        empty_text = text_1(texts_map[language]["no_products"], color="#6B7280")
        empty_text.paddings = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

        empty_container = VStack(
            [empty_text],
            padding=16,
            width=dv.DivMatchParentSize(),
        )
        return dv.make_div(empty_container)

    logger.info(
        "Creating product state elements", products_count=len(products_list_input)
    )
    # Create product state elements
    product_states = []
    for index, product in enumerate(products_list_input):
        logger.debug(
            "Processing product",
            product_id=product.id,
            product_name=product.name,
            index=index,
        )
        product_state = make_product_state(product, index, language, chat_id, api_key)
        product_states.append(product_state)

    logger.info(
        "Creating main container with product states", states_count=len(product_states)
    )
    # Main container holding all products using VStack
    main_container = VStack(
        product_states,
        padding=16,
        width=dv.DivMatchParentSize(),
    )

    logger.info("Converting to div and saving output")
    div = dv.make_div(main_container)
    with open("logs/json/build_products_list_widget.json", "w", encoding="utf-8") as f:
        json.dump(div, f, indent=2, ensure_ascii=False)

    logger.info("Successfully built products list widget")
    return div


if __name__ == "__main__":
    # ----------------------------------
    #  Test data
    # ----------------------------------

    payload = {
        "id": "55079",
        "remote_id": "67932",
        "name_uz": "iPhone 16 Pro 128GB Desert Titanium Smartfoni",
        "name_ru": "Смартфон iPhone 16 Pro 128GB Desert Titanium",
        "slug": "smartfon-iphone-16-pro-128gb-desert-titanium-55079",
        "brand": {
            "id": 17,
            "name": "Apple",
            "name_ru": "Apple",
            "name_uz": "Apple",
            "default_lang": "uz",
        },
        "main_categories": [
            {
                "id": 5499,
                "name": "Smartfonlar",
                "slug": "smartfony",
                "depth": 3,
                "parent": {
                    "id": 5473,
                    "name": "Smartfonlar va telefonlar",
                    "slug": "smartfony-i-telefony",
                    "depth": 2,
                    "parent": {"id": 5243},
                },
                "exist_children": True,
                "product_count": 1524,
                "order": 4,
                "status": 1,
                "created_at": "12-07-2024 15:57:54",
                "updated_at": "02-05-2025 10:45:14",
            },
            {
                "id": 5473,
                "name": "Smartfonlar va telefonlar",
                "slug": "smartfony-i-telefony",
                "depth": 2,
                "parent": {
                    "id": 5243,
                    "name": "Elektronikaa",
                    "slug": "elektronika",
                    "depth": 1,
                    "parent": None,
                },
                "exist_children": True,
                "product_count": 3217,
                "order": 10,
                "status": 1,
                "created_at": "12-07-2024 15:57:53",
                "updated_at": "09-05-2025 01:00:05",
            },
            {
                "id": 5473,
                "name": "Smartfonlar va telefonlar",
                "slug": "smartfony-i-telefony",
                "depth": 2,
                "parent": {
                    "id": 5243,
                    "name": "Elektronikaa",
                    "slug": "elektronika",
                    "depth": 1,
                    "parent": None,
                },
                "exist_children": True,
                "product_count": 3217,
                "order": 10,
                "status": 1,
                "created_at": "12-07-2024 15:57:53",
                "updated_at": "09-05-2025 01:00:05",
            },
        ],
        "short_name_uz": None,
        "short_name_ru": None,
        "main_image": {
            "mobile": "https://s3.smartbank.uz/market-test/products/secondary_images/mobile/DNpvPs686PIGc2b9v369fRuEJGyS4e.webp",
            "desktop": "https://s3.smartbank.uz/market-test/products/secondary_images/desktop/DNpvPs686PIGc2b9v369fRuEJGyS4e.webp",
        },
        "created_at": "2024-09-22 11:00:46",
        "updated_at": "2025-04-29 14:52:17",
        "count": 0,
        "tracking": False,
        "offers": [
            {
                "id": 76294,
                "original_price": 0,
                "price": 14049000,
                "3_month_price": 17139900,
                "6_month_price": 18544800,
                "9_month_price": 20933700,
                "12_month_price": 19528800,
                "18_month_price": 22478400,
                "discount": False,
                "discount_percent": 0,
                "discount_start_at": None,
                "discount_expire_at": None,
                "merchant": {
                    "id": 74,
                    "name": "Mirzayev's company",
                    "logo": "https://s3.smartbank.uz/market-test/merchants/logos/Z3WdqlbOAVVyvmOzA49fCiNU3WDGYmhnxgQ7wz4p.jpg",
                    "type": {"value": 20, "name": "XT"},
                    "status": {"value": 10, "name": "Актив"},
                    "created_at": "2024-10-17T06:40:26.000000Z",
                    "updated_at": "2025-03-27T04:18:06.000000Z",
                },
                "status": {"value": 0, "label": "Kutilmoqda"},
                "market_type": "b2b",
            },
            {
                "id": 53414,
                "original_price": 22969000,
                "price": 14049000,
                "3_month_price": 17139900,
                "6_month_price": 18544800,
                "9_month_price": 0,
                "12_month_price": 19528800,
                "18_month_price": 22478400,
                "discount": True,
                "discount_percent": 0,
                "discount_start_at": "2025-02-19 12:49:45",
                "discount_expire_at": "2026-02-20 12:49:45",
                "merchant": {
                    "id": 1,
                    "name": "Asaxiy Test",
                    "logo": "https://s3.smartbank.uz/market-test/merchants/logos/VK8yD4rdIsZJ8ltgH7WPHqEzYHh2NeVAOW7nNJYf.jpg",
                    "type": {"value": 20, "name": "XT"},
                    "status": {"value": 10, "name": "Актив"},
                    "created_at": None,
                    "updated_at": "2025-05-31T06:00:00.000000Z",
                },
                "status": {"value": 1, "label": "Faol"},
                "market_type": "b2c",
            },
            {
                "id": 76293,
                "original_price": 22960008,
                "price": 22960008,
                "3_month_price": 17139901,
                "6_month_price": 18544800,
                "9_month_price": 0,
                "12_month_price": 19528800,
                "18_month_price": 22478400,
                "discount": False,
                "discount_percent": 0,
                "discount_start_at": None,
                "discount_expire_at": None,
                "merchant": {
                    "id": 74,
                    "name": "Mirzayev's company",
                    "logo": "https://s3.smartbank.uz/market-test/merchants/logos/Z3WdqlbOAVVyvmOzA49fCiNU3WDGYmhnxgQ7wz4p.jpg",
                    "type": {"value": 20, "name": "XT"},
                    "status": {"value": 10, "name": "Актив"},
                    "created_at": "2024-10-17T06:40:26.000000Z",
                    "updated_at": "2025-03-27T04:18:06.000000Z",
                },
                "status": {"value": 1, "label": "Faol"},
                "market_type": "b2c",
            },
        ],
        "status": {"value": 1, "label": "Faol"},
        "view_count": 735,
        "order_count": 0,
        "like_count": 0,
        "rate": 5,
        "cancelled_count": 0,
    }

    products = [
        ProductItem(**payload),
        ProductItem(**payload),
        ProductItem(**payload),
    ]

    # Test the new widget format
    widget_result = build_products_list_widget(products)

    with open("logs/json/build_products.json", "w", encoding="utf-8") as f:
        json.dump(
            widget_result,
            f,
            indent=2,
            ensure_ascii=False,
        )

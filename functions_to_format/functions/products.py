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
    add_ui_to_widget,
    WidgetInput,
    TextWidget,
    create_feedback_variables,
    create_success_actions,
    create_failure_actions,
    create_success_container,
    create_error_container,
    get_feedback_text,
)
from .general.utils import save_builder_output
from models.build import BuildOutput
from conf import logger
from .general.text import build_text_widget
from tool_call_models.smartbazar import SearchProductsResponse, ProductItem
import structlog
from models.context import Context

# -------------------------------------------------------------------
#  Функция-шаблон: возвращает dv.DivState с двумя состояниями — collapsed
#  и expanded. Переключение реализовано через dv.DivAction -> SetState.
# -------------------------------------------------------------------
# import pydivkit as dv
# import json


def search_products(context: Context) -> BuildOutput:
    return get_products(context=context)


def get_products(context: Context) -> BuildOutput:
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    backend_output_model: SearchProductsResponse = SearchProductsResponse(
        **backend_output
    )
    # logger.info(backend_output_model)
    widget = Widget(
        name="products_list_widget",
        type="products_list_widget",
        order=1,
        layout="vertical",
        fields=["products", "title"],
    )

    products = backend_output_model.products

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    logger.info("Products", products=products)
    widgets = add_ui_to_widget(
        {
            build_products_list_widget: WidgetInput(
                widget=widget,
                args={
                    "products_list_input": products,
                    "language": language,
                    "chat_id": chat_id,
                    "api_key": api_key,
                },
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={
                    "text": llm_output,
                },
            ),
        },
        version,
    )
    output = BuildOutput(
        widgets_count=1,
        widgets=[w.model_dump(exclude_none=True) for w in widgets],
    )
    save_builder_output(context, output)
    return output


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

    # Collapsed state div
    collapsed_div = dv.DivContainer(
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        margins=dv.DivEdgeInsets(bottom=8),
        paddings=dv.DivEdgeInsets(left=12, right=12, top=12, bottom=12),
        border=dv.DivBorder(corner_radius=8, stroke=dv.DivStroke(color="#E5E7EB")),
        items=[
            dv.DivImage(
                image_url=main_image_mobile_url,
                width=dv.DivFixedSize(value=40),
                height=dv.DivFixedSize(value=40),
                scale=dv.DivImageScale.FILL,
            ),
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.VERTICAL,
                width=dv.DivWrapContentSize(),
                items=[
                    dv.DivText(
                        text=p.name, font_size=14, font_weight=dv.DivFontWeight.MEDIUM
                    ),
                    dv.DivText(
                        text=price_text,
                        font_size=13,
                        text_color="#6B7280",
                    ),
                ],
            ),
        ],
        actions=[
            dv.DivAction(
                log_id=f"expand_product_{p.id}_{index}",
                url=f"sample-actions://set_state?state_id=0/{product_state_id}/expanded",
            ),
            dv.DivAction(
                log_id=f"expand_product_{p.id}_{index}_div",
                url=f"div-action://set_state?state_id=0/{product_state_id}/expanded",
            ),
        ],
    )

    # Success feedback container for cart actions
    success_container = dv.DivContainer(
        id=f"success-{feedback_prefix}",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(
            f"@{{{feedback_prefix}_success_visible == 1 ? 'visible' : 'gone'}}"
        ),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=8, bottom=8),
        paddings=dv.DivEdgeInsets(top=10, bottom=10, left=12, right=12),
        background=[dv.DivSolidBackground(color="#ECFDF5")],
        border=dv.DivBorder(
            corner_radius=8, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        ),
        items=[
            dv.DivText(
                text="✅",
                font_size=14,
                margins=dv.DivEdgeInsets(right=8),
            ),
            dv.DivText(
                text=texts_map[language]["added_to_cart"],
                font_size=13,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=16,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=8, right=4),
                actions=[
                    dv.DivAction(
                        log_id=f"dismiss-success-{feedback_prefix}",
                        url=f"div-action://set_variable?name={feedback_prefix}_success_visible&value=0",
                    )
                ],
            ),
        ],
    )

    # Error feedback container for cart actions
    error_container = dv.DivContainer(
        id=f"error-{feedback_prefix}",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(
            f"@{{{feedback_prefix}_error_visible == 1 ? 'visible' : 'gone'}}"
        ),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=8, bottom=8),
        paddings=dv.DivEdgeInsets(top=10, bottom=10, left=12, right=12),
        background=[dv.DivSolidBackground(color="#FEF2F2")],
        border=dv.DivBorder(
            corner_radius=8, stroke=dv.DivStroke(color="#FECACA", width=1)
        ),
        items=[
            dv.DivText(
                text="⚠️",
                font_size=14,
                margins=dv.DivEdgeInsets(right=8),
            ),
            dv.DivText(
                text=texts_map[language]["cart_error"],
                font_size=13,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=16,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=8, right=4),
                actions=[
                    dv.DivAction(
                        log_id=f"dismiss-error-{feedback_prefix}",
                        url=f"div-action://set_variable?name={feedback_prefix}_error_visible&value=0",
                    )
                ],
            ),
        ],
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

    # Expanded state div
    expanded_div = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(corner_radius=12, stroke=dv.DivStroke(color="#E5E7EB")),
        paddings=dv.DivEdgeInsets(left=12, right=12, top=12, bottom=12),
        margins=dv.DivEdgeInsets(bottom=8),
        variables=[
            dv.IntegerVariable(name=f"{feedback_prefix}_success_visible", value=0),
            dv.IntegerVariable(name=f"{feedback_prefix}_error_visible", value=0),
        ],
        items=[
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=[
                    dv.DivImage(
                        image_url=main_image_mobile_url,
                        width=dv.DivFixedSize(value=40),
                        height=dv.DivFixedSize(value=40),
                        scale=dv.DivImageScale.FILL,
                    ),
                    dv.DivContainer(
                        orientation=dv.DivContainerOrientation.VERTICAL,
                        width=dv.DivWrapContentSize(),
                        items=[
                            dv.DivText(
                                text=p.name,
                                font_size=14,
                                font_weight=dv.DivFontWeight.MEDIUM,
                            ),
                            dv.DivText(
                                text=price_text,
                                font_size=13,
                                text_color="#6B7280",
                            ),
                        ],
                    ),
                ],
                actions=[
                    dv.DivAction(
                        log_id=f"collapse_product_{p.id}_{index}",
                        url=f"sample-actions://set_state?state_id=0/{product_state_id}/collapsed",
                    ),
                    dv.DivAction(
                        log_id=f"collapse_product_{p.id}_{index}_div",
                        url=f"div-action://set_state?state_id=0/{product_state_id}/collapsed",
                    ),
                ],
            ),
            dv.DivImage(
                image_url=main_image_mobile_url,
                width=dv.DivMatchParentSize(),
                height=dv.DivWrapContentSize(),
                margins=dv.DivEdgeInsets(top=12),
                scale=dv.DivImageScale.FIT,
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                alignment_vertical=dv.DivAlignmentVertical.CENTER,
            ),
            dv.DivText(
                text=p.name,
                font_size=13,
                text_color="#374151",
                margins=dv.DivEdgeInsets(top=8),
            ),
            dv.DivText(
                text=f"⭐ {p.rate or 0}",
                font_size=11,
                text_color="#6B7280",
                margins=dv.DivEdgeInsets(top=4),
            ),
            dv.DivText(
                text=installment_price_text,
                font_size=11,
                text_color="#DB2777",
                background=[dv.DivSolidBackground(color="#FCE7F3")],
                paddings=dv.DivEdgeInsets(left=6, top=4, right=6, bottom=4),
                margins=dv.DivEdgeInsets(top=6),
                border=dv.DivBorder(
                    corner_radius=4, stroke=dv.DivStroke(color="#FCE7F3")
                ),
            ),
            # Feedback containers
            success_container,
            error_container,
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                margins=dv.DivEdgeInsets(top=12),
                width=dv.DivMatchParentSize(),
                content_alignment_horizontal=(
                    dv.DivContentAlignmentHorizontal.SPACE_BETWEEN
                    if p.offer_id
                    else dv.DivContentAlignmentHorizontal.CENTER
                ),
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                id=cart_container,
                items=(  # pyright: ignore[reportArgumentType]
                    [
                        (
                            dv.DivText(
                                text=texts_map[language]["add"],
                                border=dv.DivBorder(
                                    corner_radius=8,
                                    stroke=dv.DivStroke(color="#3B82F6"),
                                ),
                                text_color="#2563EB",
                                height=dv.DivFixedSize(value=36),
                                width=dv.DivMatchParentSize(),
                                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                alignment_vertical=dv.DivAlignmentVertical.CENTER,
                                text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
                                paddings=dv.DivEdgeInsets(left=16, right=16),
                                margins=(
                                    dv.DivEdgeInsets(right=4)
                                    if p.offer_id
                                    else dv.DivEdgeInsets()
                                ),
                                actions=[
                                    dv.DivAction(
                                        url="divkit://send-request",
                                        log_id=f"add_to_cart_{p.id}_{index}",
                                        typed=dv.DivActionSubmit(
                                            container_id=cart_container,
                                            request=dv.DivActionSubmitRequest(
                                                url=f"https://smarty.smartbank.uz/chat/v3/tools/call?function_name=add_product_to_cart&chat_id={chat_id}&arguments={json.dumps({'offer_id': p.offer_id, 'quantity': 1})}",
                                                method=dv.RequestMethod.POST,
                                                headers=[
                                                    dv.RequestHeader(
                                                        name="api-key", value=api_key
                                                    )
                                                ],
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
                                ],
                            )
                            if p.offer_id
                            else None
                        ),
                        dv.DivText(
                            text=texts_map[language]["hide"],
                            border=dv.DivBorder(
                                corner_radius=8, stroke=dv.DivStroke(color="#D1D5DB")
                            ),
                            text_color="#6B7280",
                            height=dv.DivFixedSize(value=36),
                            width=dv.DivMatchParentSize(),
                            alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                            alignment_vertical=dv.DivAlignmentVertical.CENTER,
                            text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                            text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
                            paddings=dv.DivEdgeInsets(left=16, right=16),
                            margins=(
                                dv.DivEdgeInsets(left=4)
                                if p.offer_id
                                else dv.DivEdgeInsets()
                            ),
                            actions=[
                                dv.DivAction(
                                    log_id=f"collapse_from_button_{p.id}_{index}",
                                    url=f"sample-actions://set_state?state_id=0/{product_state_id}/collapsed",
                                ),
                                dv.DivAction(
                                    log_id=f"collapse_from_button_{p.id}_{index}_div",
                                    url=f"div-action://set_state?state_id=0/{product_state_id}/collapsed",
                                ),
                            ],
                        ),
                    ]
                    if p.offer_id
                    else [
                        dv.DivText(
                            text=texts_map[language]["hide"],
                            border=dv.DivBorder(
                                corner_radius=8, stroke=dv.DivStroke(color="#D1D5DB")
                            ),
                            text_color="#6B7280",
                            height=dv.DivFixedSize(value=36),
                            width=dv.DivMatchParentSize(),
                            alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                            alignment_vertical=dv.DivAlignmentVertical.CENTER,
                            text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                            text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
                            paddings=dv.DivEdgeInsets(left=16, right=16),
                            margins=dv.DivEdgeInsets(),
                            actions=[
                                dv.DivAction(
                                    log_id=f"collapse_from_button_{p.id}_{index}",
                                    url=f"sample-actions://set_state?state_id=0/{product_state_id}/collapsed",
                                ),
                                dv.DivAction(
                                    log_id=f"collapse_from_button_{p.id}_{index}_div",
                                    url=f"div-action://set_state?state_id=0/{product_state_id}/collapsed",
                                ),
                            ],
                        ),
                    ]
                ),
            ),
        ],
    )

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
    """Build products list widget using pydivkit SDK classes"""
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
        empty_div = dv.DivText(
            text=texts_map[language]["no_products"],
            paddings=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
        )

        return dv.make_div(
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.VERTICAL,
                width=dv.DivMatchParentSize(),
                paddings=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
                items=[empty_div],
            )
        )

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
    # Main container holding all products
    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(),
        paddings=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
        items=product_states,
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

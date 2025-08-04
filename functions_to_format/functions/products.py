import os
import sys

sys.path.append("/home/aslonhamidov/Desktop/work/ui_server")
import pydivkit as dv
from datetime import timedelta
import json, sys
from pydantic import BaseModel
from typing import List, Optional
from functions_to_format.functions.general import (
    Widget,
    add_ui_to_widget,
    WidgetInput,
    TextWidget,
)
from models.build import BuildOutput
from conf import logger
from .general.text import build_text_widget
from tool_call_models.smartbazar import SearchProductsResponse, ProductItem
# -------------------------------------------------------------------
#  Функция-шаблон: возвращает dv.DivState с двумя состояниями — collapsed
#  и expanded. Переключение реализовано через dv.DivAction -> SetState.
# -------------------------------------------------------------------
# import pydivkit as dv
# import json


def search_products(*args, **kwargs) -> BuildOutput:
    return get_products(*args, **kwargs)


def get_products(
    llm_output: str, backend_output: dict, version: str = "v3"
) -> BuildOutput:
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

    products = backend_output_model.items

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={
                    "text": llm_output,
                },
            ),
            build_products_list_widget: WidgetInput(
                widget=widget,
                args={"products_list_input": products},
            ),
        },
        version,
    )
    return BuildOutput(
        widgets_count=1,
        widgets=[w.model_dump(exclude_none=True) for w in widgets],
    )


def make_product_state(p: ProductItem, index: int):
    """Create a product state element using pydivkit SDK classes"""
    product_state_id = f"product_{p.id}_{index}"  # Make unique by adding index

    # Safely get image URLs
    main_image_mobile_url = ""
    main_image_desktop_url = ""
    if isinstance(p.main_image, dict):
        main_image_mobile_url = p.main_image.get("mobile", "")
        main_image_desktop_url = p.main_image.get("desktop", "")
    elif isinstance(p.main_image, str):
        main_image_mobile_url = p.main_image
        main_image_desktop_url = p.main_image

    if not main_image_mobile_url and main_image_desktop_url:
        main_image_mobile_url = main_image_desktop_url
    elif not main_image_desktop_url and main_image_mobile_url:
        main_image_desktop_url = main_image_mobile_url

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
                    dv.DivText(text=p.name_ru, font_size=14, font_weight=dv.DivFontWeight.MEDIUM),
                    dv.DivText(
                        text=f"{p.offers[0].price if p.offers else ''} сумм",
                        font_size=13,
                        text_color="#6B7280",
                    ),
                ],
            ),
            # dv.DivText(
            #     text="⌄",  # Changed to a down arrow
            #     font_size=24,
            #     text_color="#9CA3AF",
            #     width=dv.DivWrapContentSize(),
            #     alignment_horizontal=dv.DivAlignmentHorizontal.END,
            #     alignment_vertical=dv.DivAlignmentVertical.CENTER,
            #     # margins=dv.DivEdgeInsets(left="auto"),
            # ),
        ],
        actions=[
            dv.DivAction(
                log_id="expand_product",
                url=f"sample-actions://set_state?state_id=0/{product_state_id}/expanded",
            ),
            dv.DivAction(
                log_id="expand_product",
                url=f"div-action://set_state?state_id=0/{product_state_id}/expanded",
            ),
        ],
    )

    # Expanded state div
    offer_price_text = f"{p.offers[0].price if p.offers else ''} сумм"
    if p.offers and isinstance( p.offers[0].twelve_month_price, str):
        p.offers[0].twelve_month_price = int(p.offers[0].twelve_month_price)
    elif p.offers and( isinstance( p.offers[0].twelve_month_price, int) or isinstance( p.offers[0].twelve_month_price, float) ):
        if (
            p.offers
            and p.offers[0].twelve_month_price
            and p.offers[0].twelve_month_price > 0
        ):
            offer_price_text = f"{p.offers[0].twelve_month_price} сумм x 12 мес"

    expanded_div = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(corner_radius=12, stroke=dv.DivStroke(color="#E5E7EB")),
        paddings=dv.DivEdgeInsets(left=12, right=12, top=12, bottom=12),
        margins=dv.DivEdgeInsets(bottom=8),
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
                                text=p.name_ru, font_size=14, font_weight=dv.DivFontWeight.MEDIUM
                            ),
                            dv.DivText(
                                text=f"{p.offers[0].price if p.offers else ''} сумм",
                                font_size=13,
                                text_color="#6B7280",
                            ),
                        ],
                    ),
                    # dv.DivText(
                    #     text="⌃",  # Changed to an up arrow
                    #     font_size=24,
                    #     text_color="#9CA3AF",
                    #     width=dv.DivWrapContentSize(),
                    #     alignment_horizontal=dv.DivAlignmentHorizontal.END,
                    #     alignment_vertical=dv.DivAlignmentVertical.CENTER,
                    #     margins=dv.DivEdgeInsets(),
                    # ),
                ],
                actions=[
                    dv.DivAction(
                        log_id="collapse_product",
                        url=f"sample-actions://set_state?state_id=0/{product_state_id}/collapsed",
                    ),
                    dv.DivAction(
                        log_id="collapse_product",
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
                text=p.name_ru,
                font_size=13,
                text_color="#374151",
                margins=dv.DivEdgeInsets(top=8),
            ),
            dv.DivText(
                text=f"⭐ {p.rate}",
                font_size=11,
                text_color="#6B7280",
                margins=dv.DivEdgeInsets(top=4),
            ),
            dv.DivText(
                text=offer_price_text,
                font_size=11,
                text_color="#DB2777",
                background=[dv.DivSolidBackground(color="#FCE7F3")],
                paddings=dv.DivEdgeInsets(left=6, top=4, right=6, bottom=4),
                margins=dv.DivEdgeInsets(top=6),
                border=dv.DivBorder(
                    corner_radius=4, stroke=dv.DivStroke(color="#FCE7F3")
                ),
            ),
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                margins=dv.DivEdgeInsets(top=12),
                width=dv.DivMatchParentSize(),
                content_alignment_horizontal=dv.DivContentAlignmentHorizontal.SPACE_BETWEEN,
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                items=[
                    dv.DivText(
                        text="Подробнее",
                        border=dv.DivBorder(
                            corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
                        ),
                        text_color="#2563EB",
                        height=dv.DivFixedSize(value=36),
                        width=dv.DivMatchParentSize(),
                        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                        alignment_vertical=dv.DivAlignmentVertical.CENTER,
                        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                        text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
                        paddings=dv.DivEdgeInsets(left=16, right=16),
                        margins=dv.DivEdgeInsets(right=4),
                        actions=[
                            dv.DivAction(
                                log_id="buy_product",
                                url=f"sample-actions://redirect?url=https://smartbazar.uz/product/{p.id}",
                            ),
                            dv.DivAction(
                                log_id="buy_product",
                                url=f"div-action://redirect?url=https://smartbazar.uz/product/{p.id}",
                            ),
                        ],
                    ),
                    dv.DivText(
                        text="Скрыть",
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
                        margins=dv.DivEdgeInsets(left=4),
                        actions=[
                            dv.DivAction(
                                log_id="collapse_from_button",
                                url=f"sample-actions://set_state?state_id=0/{product_state_id}/collapsed",
                            ),
                            dv.DivAction(
                                log_id="collapse_from_button",
                                url=f"div-action://set_state?state_id=0/{product_state_id}/collapsed",
                            ),
                        ],
                    ),
                ],
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


def build_products_list_widget(products_list_input: List[ProductItem]):
    """Build products list widget using pydivkit SDK classes"""
    card_log_id = "products_list_card"

    if not products_list_input:
        empty_div = dv.DivText(
            text="No products to display.",
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

    # Create product state elements
    product_states = []
    for index, product in enumerate(products_list_input):
        product_state = make_product_state(product, index)
        product_states.append(product_state)

    # Main container holding all products
    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(),
        paddings=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
        items=product_states,
    )

    div = dv.make_div(main_container)
    with open("build_products_list_widget.json", "w", encoding="utf-8") as f:
        json.dump(div, f, indent=2, ensure_ascii=False)

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

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(
            widget_result,
            f,
            indent=2,
            ensure_ascii=False,
        )

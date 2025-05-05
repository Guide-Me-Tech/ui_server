# pip install pydv.divkit==1.2.0
# from pydv.divkit.core import *
import pydivkit as dv
from datetime import timedelta
import json, sys
from pydantic import BaseModel
from typing import List, Optional


# -------------------------------------------------------------------
#  Функция-шаблон: возвращает dv.DivState с двумя состояниями — collapsed
#  и expanded. Переключение реализовано через dv.DivAction -> SetState.
# -------------------------------------------------------------------
# import pydivkit as dv
# import json


class Product(BaseModel):
    id: str
    title: str
    price: str
    img: str
    desc: str
    rating: str
    installment: str
    primary_button: str


class ProductsListInput(BaseModel):
    products: List[Product]
    title: Optional[str] = "Products"


def make_product_state(p: Product):
    card_id = f"card-{p.id}"

    # --- заголовок для "свернуто" ---
    header_collapsed = dv.DivContainer(
        orientation="horizontal",
        items=[
            dv.DivImage(
                image_url=p.img,
                width=dv.DivFixedSize(value=40),
                height=dv.DivFixedSize(value=40),
                scale=dv.DivImageScale("fill"),
            ),
            dv.DivContainer(
                orientation="vertical",
                items=[
                    dv.DivText(text=p.title, font_size=14, font_weight="medium"),
                    dv.DivText(text=p.price, font_size=13, text_color="#6B7280"),
                ],
            ),
            dv.DivText(text="›", font_size=20, text_color="#9CA3AF"),
        ],
        action=dv.DivAction(
            log_id="expand",
            url=f"div-action://set_state?state_id={card_id}/expanded",
        ),
    )

    # --- заголовок для "развёрнуто" ---
    header_expanded = dv.DivContainer(
        orientation="horizontal",
        items=[
            dv.DivImage(
                image_url=p.img,
                width=dv.DivFixedSize(value=40),
                height=dv.DivFixedSize(value=40),
                scale=dv.DivImageScale("fill"),
            ),
            dv.DivContainer(
                orientation="vertical",
                items=[
                    dv.DivText(text=p.title, font_size=14, font_weight="medium"),
                    dv.DivText(text=p.price, font_size=13, text_color="#6B7280"),
                ],
            ),
            dv.DivText(text="˅", font_size=20, text_color="#9CA3AF"),
        ],
        action=dv.DivAction(
            log_id="collapse",
            url=f"div-action://set_state?state_id={card_id}/collapsed",
        ),
    )

    collapsed = dv.DivContainer(
        items=[header_collapsed],
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        margins=dv.DivEdgeInsets(bottom=8),
    )

    expanded = dv.DivContainer(
        orientation="vertical",
        items=[
            header_expanded,
            dv.DivImage(
                image_url=p.img,
                width=dv.DivMatchParentSize(),
                height=dv.DivFixedSize(value=160),
                margins=dv.DivEdgeInsets(top=12),
            ),
            dv.DivText(text=p.desc, font_size=13, text_color="#374151"),
            dv.DivText(text=p.rating, font_size=11, text_color="#6B7280"),
            dv.DivText(
                text=p.installment,
                font_size=11,
                text_color="#DB2777",
                background=[dv.DivSolidBackground(color="#FCE7F3")],
                paddings=dv.DivEdgeInsets(left=6, top=4),
                margins=dv.DivEdgeInsets(top=6),
            ),
            dv.DivContainer(
                orientation="horizontal",
                items=[
                    dv.DivText(
                        text=p.primary_button,
                        id="primary",
                        border=dv.DivBorder(
                            corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
                        ),
                        text_color="#2563EB",
                        height=dv.DivFixedSize(value=36),
                    ),
                    dv.DivText(
                        text="Скрыть",
                        action=dv.DivAction(
                            log_id="collapse-btn",
                            url=f"div-action://set_state?state_id={card_id}/collapsed",
                        ),
                        border=dv.DivBorder(
                            corner_radius=8, stroke=dv.DivStroke(color="#D1D5DB")
                        ),
                        text_color="#6B7280",
                        height=dv.DivFixedSize(value=36),
                        margins=dv.DivEdgeInsets(left=8),
                    ),
                ],
                margins=dv.DivEdgeInsets(top=12),
            ),
        ],
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(corner_radius=12, stroke=dv.DivStroke(color="#E5E7EB")),
        paddings=dv.DivEdgeInsets(left=16, right=16, bottom=16, top=16),
        margins=dv.DivEdgeInsets(bottom=8),
    )

    # ★ здесь снова id, не state_id
    return dv.DivState(
        id=card_id,  # ★ правильное имя поля
        states=[
            dv.DivStateState(state_id="collapsed", div=collapsed),
            dv.DivStateState(state_id="expanded", div=expanded),
        ],
        default_state_id="collapsed",
    )


def build_products_list_widget(backend_output: dict, llm_output: str):
    # Parse input data
    input_data = ProductsListInput(**backend_output)

    # Create product state widgets
    div_states = [make_product_state(product) for product in input_data.products]

    # Create data states
    data_states = [
        dv.DivDataState(state_id=str(i), div=s) for i, s in enumerate(div_states)
    ]

    # Create the final DivData
    data = dv.DivData(log_id="product_list", states=data_states)

    # Return the widget as a JSON-serializable object
    return data.dict()


if __name__ == "__main__":

    # ----------------------------------
    #  Данные товаров (можно брать из БД)
    # ----------------------------------
    products = [
        Product(
            id="0",
            title="Смартфон Nothing Phone",
            price="3 953 000 сум",
            img="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6j3LinJbdeph2V4vBVa-IDPHlsStt8LjCQw&s",
            desc="Nothing Phone (1) 8/256 ГБ…",
            rating="⭐ 4.1 / 12 отзывов",
            installment="1 340 000 сум × 12 мес",
            primary_button="Good",
        ),
        Product(
            id="1",
            title="New Product 1",
            price="1 000 000 сум",
            img="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6j3LinJbdeph2V4vBVa-IDPHlsStt8LjCQw&s",
            desc="New Product 1 Description…",
            rating="⭐ 4.5 / 20 отзывов",
            installment="500 000 сум × 6 мес",
            primary_button="Buy Now",
        ),
        Product(
            id="2",
            title="New Product 2",
            price="2 000 000 сум",
            img="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6j3LinJbdeph2V4vBVa-IDPHlsStt8LjCQw&s",
            desc="New Product 2 Description…",
            rating="⭐ 4.8 / 30 отзывов",
            installment="1 000 000 сум × 12 мес",
            primary_button="Add to Cart",
        ),
    ]
    div_states = [make_product_state(p) for p in products]

    # root_div = dv.DivContainer(
    #     orientation="vertical",
    #     width=dv.DivMatchParentSize(),
    #     items=[make_product_state(p) for p in products],
    #     paddings=dv.DivEdgeInsets(left=16, right=16, bottom=16, top=16),
    # )
    data_states = [
        dv.DivDataState(
            state_id=i, div=s
        )  # `state_id` тут просто индекс (можно и str(id))
        for i, s in enumerate(div_states)
    ]
    # Формируем итоговый DivData
    data = dv.DivData(log_id="product_list", states=data_states)

    with open("jsons/products.json", "w", encoding="utf-8") as f:
        # json.dump(dv.make_div(root_div), f, indent=2, ensure_ascii=False)
        # json.dump(data.dict(), f, indent=2, ensure_ascii=False)
        json.dump(
            {
                "log_id": "test_card",
                "card": make_product_state(products[0]).dict(),  # только одна карточка
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

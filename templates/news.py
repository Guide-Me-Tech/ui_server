import pydivkit as dv
import json


def news_item(title, source, time, image_url, url):
    return dv.DivContainer(
        orientation="horizontal",
        alignment_vertical="center",
        items=[
            dv.DivContainer(
                orientation="vertical",
                # width=dv.DivWeight(1),
                items=[
                    dv.DivText(
                        text=title,
                        font_size=14,
                        font_weight="medium",
                        text_color="#FFFFFF",
                        max_lines=1,
                        # ellipsis=dv.DivTextEllipsis(),
                    ),
                    dv.DivText(
                        text=f"{source} · {time}",
                        font_size=12,
                        text_color="#D1D5DB",
                        margins=dv.DivEdgeInsets(top=2),
                        max_lines=1,
                        # ellipsis=dv.DivTextEllipsis(),
                    ),
                ],
            ),
            dv.DivImage(
                image_url=image_url,
                width=dv.DivFixedSize(value=36),
                height=dv.DivFixedSize(value=36),
                scale=dv.DivImageScale.FILL,
                border=dv.DivBorder(corner_radius=8),
                margins=dv.DivEdgeInsets(left=12),
            ),
        ],
        margins=dv.DivEdgeInsets(top=12),
        action=dv.DivAction(log_id="open-news", url=url),  # this will open the web page
    )


if __name__ == "__main__":

    news = [
        news_item(
            title="Tramp Chris Wright kompaniyasi rahbarini tanladi...",
            source="Kun.uz",
            time="1s",
            image_url="https://humocard.uz/bitrix/templates/main/img/card2.png",
            url="https://a3n.uz",
        ),
        news_item(
            title="Soliqchilar endi soliqdan qocha olmaydi.",
            source="Daryo",
            time="2s",
            image_url="https://humocard.uz/bitrix/templates/main/img/card2.png",
            url="https://a3n.uz",
        ),
        news_item(
            title="O'zbekistonda yangi soliq tizimi joriy etilmoqda...",
            source="Gazeta.uz",
            time="3s",
            image_url="https://humocard.uz/bitrix/templates/main/img/card2.png",
            url="https://a3n.uz",
        ),
    ]
    items = [
        # Header
        dv.DivContainer(
            orientation="horizontal",
            items=[
                # dv.DivImage(
                #     image_url="https://www.gstatic.com/images/branding/product/1x/googlenews_512dp.png",
                #     width=dv.DivFixedSize(value=18),
                #     height=dv.DivFixedSize(value=18),
                #     scale=dv.DivImageScale.FIT,
                #     margins=dv.DivEdgeInsets(right=6),
                # ),
                dv.DivText(
                    text="TOP NEWS",
                    font_size=12,
                    font_weight="bold",
                    text_color="#9CA3AF",
                    letter_spacing=0.5,
                ),
            ],
        ),
    ]
    items.extend(news)

    root = dv.DivContainer(
        orientation="vertical",
        background=[dv.DivSolidBackground(color="#1F2937")],  # dark gray background
        border=dv.DivBorder(corner_radius=16),
        paddings=dv.DivEdgeInsets(
            top=12, bottom=12, left=16, right=16
        ),  # внутренние отступы
        margins=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),  # внешние отступы
        items=items,
    )

    # Save to JSON
    with open("jsons/news_widget.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)

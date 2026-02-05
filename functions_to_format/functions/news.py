import pydivkit as dv
from pydivkit.core import Expr
import json
from pydantic import BaseModel
from typing import List

from functions_to_format.functions.general.utils import save_builder_output
from .general import Widget, add_ui_to_widget, WidgetInput
from models.build import BuildOutput
from functions_to_format.functions.general.const_values import LanguageOptions
from conf import logger
import structlog
from models.context import Context


# Feedback texts for news actions
NEWS_FEEDBACK_TEXTS = {
    LanguageOptions.RUSSIAN: {
        "opening": "Открываем новость...",
        "opened": "Новость открыта",
        "error": "Не удалось открыть новость",
    },
    LanguageOptions.ENGLISH: {
        "opening": "Opening article...",
        "opened": "Article opened",
        "error": "Failed to open article",
    },
    LanguageOptions.UZBEK: {
        "opening": "Yangilik ochilmoqda...",
        "opened": "Yangilik ochildi",
        "error": "Yangilikni ochib bo'lmadi",
    },
}


class NewsItem(BaseModel):
    title: str
    source: str
    time: str
    image_url: str
    url: str


class NewsWidgetInput(BaseModel):
    news_items: List[NewsItem]
    header_text: str = "TOP NEWS"


def get_news(context: Context) -> BuildOutput:
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    news_widget_input = NewsWidgetInput(**backend_output)
    widget = Widget(
        name="news_widget",
        type="news_widget",
        order=1,
        layout="vertical",
        fields=["news_items", "header_text"],
    )
    widgets = add_ui_to_widget(
        {
            build_news_widget: WidgetInput(
                widget=widget,
                args={"news_widget_input": news_widget_input},
            ),
        },
        version,
    )
    output = BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def news_item(
    title: str,
    source: str,
    time: str,
    image_url: str,
    url: str,
    index: int = 0,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Create a news item container with action handling and feedback.
    
    Args:
        title: News article title
        source: News source name
        time: Publication time
        image_url: Thumbnail image URL
        url: Article URL to open
        index: Item index for unique log IDs
        language: Language for localization
        
    Returns:
        DivContainer for the news item
    """
    feedback_texts = NEWS_FEEDBACK_TEXTS.get(language, NEWS_FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    item_id = f"news-item-{index}"
    
    return dv.DivContainer(
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        alignment_vertical=dv.DivAlignmentVertical.CENTER,
        items=[
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.VERTICAL,
                items=[
                    dv.DivText(
                        text=title,
                        font_size=14,
                        font_weight=dv.DivFontWeight.MEDIUM,
                        text_color="#FFFFFF",
                        max_lines=1,
                    ),
                    dv.DivText(
                        text=f"{source} · {time}",
                        font_size=12,
                        text_color="#D1D5DB",
                        margins=dv.DivEdgeInsets(top=2),
                        max_lines=1,
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
        actions=[
            # Main action to open news URL
            dv.DivAction(
                log_id=f"open-news-{index}",
                url=url,
                payload={
                    "news_title": title,
                    "news_source": source,
                    "news_url": url,
                },
            ),
            # Success feedback action
            dv.DivAction(
                log_id=f"open-news-{index}-success",
                url="div-action://set_variable?name=news_opened&value=1",
            ),
        ],
    )


def build_news_widget(
    news_widget_input: NewsWidgetInput,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Build the news widget with feedback handling for news item actions.
    
    Args:
        news_widget_input: Input data containing news items and header text
        language: Language for localization
        
    Returns:
        DivKit JSON for the news widget
    """
    feedback_texts = NEWS_FEEDBACK_TEXTS.get(language, NEWS_FEEDBACK_TEXTS[LanguageOptions.ENGLISH])

    # Create news items with proper indexing
    news = [
        news_item(
            title=item.title,
            source=item.source,
            time=item.time,
            image_url=item.image_url,
            url=item.url,
            index=idx,
            language=language,
        )
        for idx, item in enumerate(news_widget_input.news_items)
    ]

    # Success feedback container for news opened
    success_container = dv.DivContainer(
        id="news-success-container",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{news_opened == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=8),
        paddings=dv.DivEdgeInsets(top=8, bottom=8, left=12, right=12),
        background=[dv.DivSolidBackground(color="#065F46")],
        border=dv.DivBorder(
            corner_radius=8, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        ),
        items=[
            dv.DivText(
                text="✅",
                font_size=13,
                margins=dv.DivEdgeInsets(right=8),
            ),
            dv.DivText(
                text=feedback_texts["opened"],
                font_size=12,
                text_color="#ECFDF5",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=14,
                text_color="#ECFDF5",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=8),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-news-success",
                        url="div-action://set_variable?name=news_opened&value=0",
                    )
                ],
            ),
        ],
    )

    items = [
        # Header
        dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            items=[
                dv.DivText(
                    text=news_widget_input.header_text,
                    font_size=12,
                    font_weight=dv.DivFontWeight.BOLD,
                    text_color="#9CA3AF",
                    letter_spacing=0.5,
                ),
            ],
        ),
    ]
    items.extend(news)
    items.append(success_container)

    root = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        background=[dv.DivSolidBackground(color="#1F2937")],  # dark gray background
        border=dv.DivBorder(corner_radius=16),
        paddings=dv.DivEdgeInsets(
            top=12, bottom=12, left=16, right=16
        ),
        margins=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
        variables=[
            dv.IntegerVariable(name="news_opened", value=0),
        ],
        items=items,
    )

    return dv.make_div(root)


if __name__ == "__main__":
    news = [
        news_item(
            title="Trump elige a Chris Wright, CEO de...",
            source="CNN en Español",
            time="1h",
            image_url="https://humocard.uz/bitrix/templates/main/img/card2.png",
            url="https://a3n.uz",
        ),
        news_item(
            title="Matt Gaetz será el fiscal general...",
            source="El Nacional",
            time="2h",
            image_url="https://humocard.uz/bitrix/templates/main/img/card2.png",
            url="https://a3n.uz",
        ),
    ]
    items = [
        # Header
        dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
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
                    font_weight=dv.DivFontWeight.BOLD,
                    text_color="#9CA3AF",
                    letter_spacing=0.5,
                ),
            ],
        ),
    ]
    items.extend(news)

    root = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        background=[dv.DivSolidBackground(color="#1F2937")],  # dark gray background
        border=dv.DivBorder(corner_radius=16),
        paddings=dv.DivEdgeInsets(
            top=12, bottom=12, left=16, right=16
        ),  # внутренние отступы
        margins=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),  # внешние отступы
        items=items,
    )

    # Save to JSON
    with open("logs/json/news_widget.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)

import pydivkit as dv
from pydivkit.core import Expr
import json
from pydantic import BaseModel
from typing import List

from .general import Widget, WidgetInput
from functions_to_format.functions.general.const_values import LanguageOptions
from conf import logger
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


class GetNews(FunctionStrategy):
    """Strategy for building news UI."""

    def build_widget_inputs(self, context):
        news_widget_input = NewsWidgetInput(**context.backend_output)
        return {
            build_news_widget: WidgetInput(
                widget=Widget(
                    name="news_widget",
                    type="news_widget",
                    order=1,
                    layout="vertical",
                    fields=["news_items", "header_text"],
                ),
                args={"news_widget_input": news_widget_input},
            ),
        }


get_news = GetNews()


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
    Create a news item container with action handling and feedback using smarty_ui.

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
    feedback_texts = NEWS_FEEDBACK_TEXTS.get(
        language, NEWS_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )
    item_id = f"news-item-{index}"

    # Title text using text_1
    title_text = text_1(title, color="#FFFFFF")
    title_text.font_weight = dv.DivFontWeight.MEDIUM
    title_text.max_lines = 1

    # Source and time using caption_1
    source_text = caption_1(f"{source} · {time}", color="#D1D5DB")
    source_text.margins = dv.DivEdgeInsets(top=2)
    source_text.max_lines = 1

    # Text container using VStack
    text_container = VStack([title_text, source_text])

    # News thumbnail image
    news_image = dv.DivImage(
        image_url=image_url,
        width=dv.DivFixedSize(value=36),
        height=dv.DivFixedSize(value=36),
        scale=dv.DivImageScale.FILL,
        border=dv.DivBorder(corner_radius=8),
        margins=dv.DivEdgeInsets(left=12),
    )

    # Main container using HStack
    container = HStack(
        [text_container, news_image],
        alignment=dv.DivContentAlignmentVertical.CENTER,
    )
    container.margins = dv.DivEdgeInsets(top=12)
    container.actions = [
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
    ]

    return container


def build_news_widget(
    news_widget_input: NewsWidgetInput,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Build the news widget with feedback handling using smarty_ui components.

    Args:
        news_widget_input: Input data containing news items and header text
        language: Language for localization

    Returns:
        DivKit JSON for the news widget
    """
    feedback_texts = NEWS_FEEDBACK_TEXTS.get(
        language, NEWS_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

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

    # Success feedback container for news opened using smarty_ui
    success_icon = caption_1("✅", color="#ECFDF5")
    success_icon.margins = dv.DivEdgeInsets(right=8)

    success_text = caption_1(feedback_texts["opened"], color="#ECFDF5")
    success_text.font_weight = dv.DivFontWeight.MEDIUM
    success_text.width = dv.DivMatchParentSize(weight=1)

    dismiss_btn = caption_1("✕", color="#ECFDF5")
    dismiss_btn.font_weight = dv.DivFontWeight.BOLD
    dismiss_btn.paddings = dv.DivEdgeInsets(left=8)
    dismiss_btn.actions = [
        dv.DivAction(
            log_id="dismiss-news-success",
            url="div-action://set_variable?name=news_opened&value=0",
        )
    ]

    success_container = HStack(
        [success_icon, success_text, dismiss_btn],
        alignment=dv.DivContentAlignmentVertical.CENTER,
        padding=8,
        background="#065F46",
        corner_radius=8,
        width=dv.DivMatchParentSize(),
    )
    success_container.id = "news-success-container"
    success_container.visibility = Expr("@{news_opened == 1 ? 'visible' : 'gone'}")
    success_container.margins = dv.DivEdgeInsets(top=8)
    success_container.border = dv.DivBorder(
        corner_radius=8, stroke=dv.DivStroke(color="#A7F3D0", width=1)
    )

    # Header using caption_2
    header_text = caption_2(news_widget_input.header_text, color="#9CA3AF")
    header_text.font_weight = dv.DivFontWeight.BOLD
    header_text.letter_spacing = 0.5

    header_container = HStack([header_text])

    items = [header_container]
    items.extend(news)
    items.append(success_container)

    # Root container using VStack
    root = VStack(
        items,
        padding=12,
        background="#1F2937",  # dark gray background
        corner_radius=16,
    )
    root.paddings = dv.DivEdgeInsets(top=12, bottom=12, left=16, right=16)
    root.margins = dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8)
    root.variables = [
        dv.IntegerVariable(name="news_opened", value=0),
    ]

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

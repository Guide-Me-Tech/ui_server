import pydivkit as dv
from pydantic import BaseModel
from functions_to_format.functions.base_strategy import FunctionStrategy
from models.widget import Widget
from functions_to_format.functions.general import WidgetInput

from smarty_ui import (
    VStack,
    HStack,
    default_theme,
    title_2,
    text_1,
    text_2,
    caption_1,
    caption_2,
)


class MortgageScheduleItem(BaseModel):
    month: int
    monthly_payment: int
    principal: int
    interest: int
    remaining_balance: int


class MortgageData(BaseModel):
    loan_amount: int
    monthly_payment: int
    total_months: int
    total_paid: int
    total_interest: int
    schedule: list[MortgageScheduleItem]


# Table styling
TABLE_HEADER_BG = "#1E293B"
TABLE_HEADER_COLOR = "#F1F5F9"
TABLE_ROW_BG = "#FFFFFF"
TABLE_ROW_ALT_BG = "#F8FAFC"
TABLE_BORDER = "#E2E8F0"
TABLE_CELL_PADDING = 8
CARD_BG = "#FFFFFF"
CARD_RADIUS = 12
SUMMARY_LABEL_COLOR = "#64748B"
SUMMARY_VALUE_COLOR = "#0F172A"

# Localization texts
TEXTS = {
    "uz": {
        "loan_amount": "Kredit summasi",
        "monthly_payment": "Oylik to'lov",
        "term_months": "Muddat (oylar)",
        "total_paid": "Jami to'langan",
        "total_interest": "Jami foiz",
        "mortgage_schedule": "Ipoteka jadvali",
        "month": "Oy",
        "payment": "To'lov",
        "principal": "Asosiy qarz",
        "interest": "Foiz",
        "balance": "Qoldiq",
        "showing_first": "Birinchi {max_rows} ta {total} oydan ko'rsatilmoqda",
        "show_full_schedule": "To'liq jadvalni ko'rsatish",
        "show_less": "Yopish",
        "currency": "so'm",
    },
    "ru": {
        "loan_amount": "Сумма кредита",
        "monthly_payment": "Ежемесячный платёж",
        "term_months": "Срок (месяцев)",
        "total_paid": "Всего выплачено",
        "total_interest": "Всего процентов",
        "mortgage_schedule": "График ипотеки",
        "month": "Месяц",
        "payment": "Платёж",
        "principal": "Основной долг",
        "interest": "Проценты",
        "balance": "Остаток",
        "showing_first": "Показаны первые {max_rows} из {total} месяцев",
        "show_full_schedule": "Показать полный график",
        "show_less": "Свернуть",
        "currency": "сум",
    },
    "en": {
        "loan_amount": "Loan amount",
        "monthly_payment": "Monthly payment",
        "term_months": "Term (months)",
        "total_paid": "Total paid",
        "total_interest": "Total interest",
        "mortgage_schedule": "Mortgage schedule",
        "month": "Month",
        "payment": "Payment",
        "principal": "Principal",
        "interest": "Interest",
        "balance": "Balance",
        "showing_first": "Showing first {max_rows} of {total} months",
        "show_full_schedule": "Show full schedule",
        "show_less": "Show less",
        "currency": "UZS",
    },
}

# Collapse trigger styling (like activity_report)
COLLAPSED_ROWS = 10
TRIGGER_BG = "#374151"
TRIGGER_TEXT_COLOR = "#F8FAFC"
TRIGGER_CHEVRON_COLOR = "#94A3B8"
TRIGGER_PADDING_V = 10
TRIGGER_PADDING_H = 12
TRIGGER_RADIUS = 8


def _get_texts(language: str) -> dict:
    """Get localized texts for the given language."""
    return TEXTS.get(language, TEXTS["en"])


def _fmt_money(value: int) -> str:
    """Format amount with thousands separator and 2 decimals."""
    return f"{value:,}"


def _schedule_row(item: MortgageScheduleItem, is_alt: bool) -> dv.DivContainer:
    """One table row for a schedule item."""
    bg = TABLE_ROW_ALT_BG if is_alt else TABLE_ROW_BG
    month_text = text_2(str(item.month), color="#334155")
    month_text.font_size = 12
    pay_text = text_2(_fmt_money(item.monthly_payment), color="#334155")
    pay_text.font_size = 12
    princ_text = text_2(_fmt_money(item.principal), color="#334155")
    princ_text.font_size = 12
    int_text = text_2(_fmt_money(item.interest), color="#334155")
    int_text.font_size = 12
    bal_text = text_2(_fmt_money(item.remaining_balance), color="#334155")
    bal_text.font_size = 12

    row = HStack(
        [
            _wrap_cell(month_text, 1),
            _wrap_cell(pay_text, 2),
            _wrap_cell(princ_text, 2),
            _wrap_cell(int_text, 2),
            _wrap_cell(bal_text, 2),
        ],
        gap=0,
        align_v="center",
    )
    row.background = [dv.DivSolidBackground(color=bg)]
    row.border = dv.DivBorder(stroke=dv.DivStroke(color=TABLE_BORDER, width=1))
    return row


def _schedule_trigger_row(
    label: str,
    chevron: str,
    state_id: str,
    target_state: str,
) -> dv.DivContainer:
    """Clickable row to toggle schedule collapsed/expanded. Tapping runs set_state."""
    set_state_url = f"div-action://set_state?state_id=0/{state_id}/{target_state}"
    label_el = dv.DivText(
        text=label,
        font_size=14,
        text_color=TRIGGER_TEXT_COLOR,
    )
    label_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(weight=1),
        items=[label_el],
    )
    chevron_el = dv.DivText(
        text=chevron,
        font_size=14,
        text_color=TRIGGER_CHEVRON_COLOR,
    )
    trigger = HStack(
        [label_container, chevron_el],
        gap=8,
        align_v="center",
        padding_left=TRIGGER_PADDING_H,
        padding_right=TRIGGER_PADDING_H,
        padding_top=TRIGGER_PADDING_V,
        padding_bottom=TRIGGER_PADDING_V,
        background=TRIGGER_BG,
        corner_radius=TRIGGER_RADIUS,
    )
    trigger.border = dv.DivBorder(
        corner_radius=TRIGGER_RADIUS,
        stroke=dv.DivStroke(color=TABLE_BORDER, width=1),
    )
    trigger.action = dv.DivAction(
        log_id=f"mortgage_schedule_{state_id}",
        url=set_state_url,
    )
    return trigger


def _wrap_cell(el: dv.DivBase, weight: int) -> dv.DivContainer:
    """Wrap element in a weighted container for table column."""
    c = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(weight=weight),
        items=[el],
        paddings=dv.DivEdgeInsets(
            left=TABLE_CELL_PADDING,
            right=TABLE_CELL_PADDING,
            top=6,
            bottom=6,
        ),
    )
    return c


def build_mortgage_widget(mortgage_data: MortgageData, language: str = "ru"):
    """Build a table-like mortgage summary and schedule using smarty_ui and pydivkit."""
    texts = _get_texts(language)
    currency = texts["currency"]

    # Summary card
    loan_label = caption_1(texts["loan_amount"], color=SUMMARY_LABEL_COLOR)
    loan_value = text_1(
        _fmt_money(mortgage_data.loan_amount) + f" {currency}",
        color=SUMMARY_VALUE_COLOR,
    )
    loan_value.font_weight = dv.DivFontWeight.BOLD
    monthly_label = caption_1(texts["monthly_payment"], color=SUMMARY_LABEL_COLOR)
    monthly_value = text_1(
        _fmt_money(mortgage_data.monthly_payment) + f" {currency}",
        color=SUMMARY_VALUE_COLOR,
    )
    monthly_value.font_weight = dv.DivFontWeight.BOLD
    term_label = caption_1(texts["term_months"], color=SUMMARY_LABEL_COLOR)
    term_value = text_1(str(mortgage_data.total_months), color=SUMMARY_VALUE_COLOR)
    term_value.font_weight = dv.DivFontWeight.BOLD
    total_label = caption_1(texts["total_paid"], color=SUMMARY_LABEL_COLOR)
    total_value = text_1(
        _fmt_money(mortgage_data.total_paid) + f" {currency}", color=SUMMARY_VALUE_COLOR
    )
    total_value.font_weight = dv.DivFontWeight.BOLD
    interest_label = caption_1(texts["total_interest"], color=SUMMARY_LABEL_COLOR)
    interest_value = text_1(
        _fmt_money(mortgage_data.total_interest) + f" {currency}",
        color=SUMMARY_VALUE_COLOR,
    )
    interest_value.font_weight = dv.DivFontWeight.BOLD

    summary_grid = VStack(
        [
            VStack([loan_label, loan_value], gap=2),
            VStack([monthly_label, monthly_value], gap=2),
            VStack([term_label, term_value], gap=2),
            VStack([total_label, total_value], gap=2),
            VStack([interest_label, interest_value], gap=2),
        ],
        gap=12,
    )
    summary_card = VStack(
        [summary_grid], padding=16, background=CARD_BG, corner_radius=CARD_RADIUS
    )
    summary_card.border = dv.DivBorder(
        corner_radius=CARD_RADIUS, stroke=dv.DivStroke(color=TABLE_BORDER, width=1)
    )
    summary_card.margins = dv.DivEdgeInsets(bottom=16)

    # Table header
    h_month = caption_1(texts["month"], color=TABLE_HEADER_COLOR)
    h_payment = caption_1(texts["payment"], color=TABLE_HEADER_COLOR)
    h_principal = caption_1(texts["principal"], color=TABLE_HEADER_COLOR)
    h_interest = caption_1(texts["interest"], color=TABLE_HEADER_COLOR)
    h_balance = caption_1(texts["balance"], color=TABLE_HEADER_COLOR)
    header_row = HStack(
        [
            _wrap_cell(h_month, 1),
            _wrap_cell(h_payment, 2),
            _wrap_cell(h_principal, 2),
            _wrap_cell(h_interest, 2),
            _wrap_cell(h_balance, 2),
        ],
        gap=0,
        align_v="center",
    )
    header_row.background = [dv.DivSolidBackground(color=TABLE_HEADER_BG)]
    header_row.border = dv.DivBorder(stroke=dv.DivStroke(color=TABLE_BORDER, width=1))

    title = title_2(texts["mortgage_schedule"])
    title.margins = dv.DivEdgeInsets(bottom=12)

    total_schedule_len = len(mortgage_data.schedule)
    max_expanded_rows = 24

    if total_schedule_len <= COLLAPSED_ROWS:
        # Small schedule: show all rows, no collapse
        rows = [
            _schedule_row(item, i % 2 == 1)
            for i, item in enumerate(mortgage_data.schedule)
        ]
        table = VStack([header_row] + rows, gap=0)
        table.border = dv.DivBorder(
            corner_radius=8,
            stroke=dv.DivStroke(color=TABLE_BORDER, width=1),
        )
        root = VStack([summary_card, title, table])
    else:
        # More than 10 rows: two states — collapsed (first 10) and expanded (up to 24)
        state_id = "mortgage_schedule_state"

        # Collapsed: header + first COLLAPSED_ROWS rows + "Show full schedule ▼"
        collapsed_rows = [
            _schedule_row(item, i % 2 == 1)
            for i, item in enumerate(mortgage_data.schedule[:COLLAPSED_ROWS])
        ]
        collapsed_table = VStack([header_row] + collapsed_rows, gap=0)
        collapsed_table.border = dv.DivBorder(
            corner_radius=8,
            stroke=dv.DivStroke(color=TABLE_BORDER, width=1),
        )
        collapsed_trigger = _schedule_trigger_row(
            label=texts["show_full_schedule"],
            chevron="▼",
            state_id=state_id,
            target_state="expanded",
        )
        collapsed_trigger.margins = dv.DivEdgeInsets(top=8)
        collapsed_view = VStack([collapsed_table, collapsed_trigger])

        # Expanded: header + all rows (up to max_expanded_rows) + "Show less ▲" + optional caption
        expanded_schedule = mortgage_data.schedule[:max_expanded_rows]
        expanded_rows = [
            _schedule_row(item, i % 2 == 1) for i, item in enumerate(expanded_schedule)
        ]
        expanded_table = VStack([header_row] + expanded_rows, gap=0)
        expanded_table.border = dv.DivBorder(
            corner_radius=8,
            stroke=dv.DivStroke(color=TABLE_BORDER, width=1),
        )
        expanded_parts = [expanded_table]
        if total_schedule_len > max_expanded_rows:
            more_text = texts["showing_first"].format(
                max_rows=max_expanded_rows, total=total_schedule_len
            )
            more = caption_2(more_text, color=SUMMARY_LABEL_COLOR)
            more.margins = dv.DivEdgeInsets(top=8)
            expanded_parts.append(more)
        expanded_trigger = _schedule_trigger_row(
            label=texts["show_less"],
            chevron="▲",
            state_id=state_id,
            target_state="collapsed",
        )
        expanded_trigger.margins = dv.DivEdgeInsets(top=8)
        expanded_parts.append(expanded_trigger)
        expanded_view = VStack(expanded_parts)

        state = dv.DivState(
            id=state_id,
            default_state_id="collapsed",
            states=[
                dv.DivStateState(state_id="collapsed", div=collapsed_view),
                dv.DivStateState(state_id="expanded", div=expanded_view),
            ],
        )
        root = VStack([summary_card, title, state])

    root.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)
    return dv.make_div(root)


class CalculateMortgage(FunctionStrategy):
    def build_widget_inputs(self, context):
        mortgage_data = MortgageData(**context.backend_output)
        language = getattr(context, "language", "ru")
        output = {
            build_mortgage_widget: WidgetInput(
                widget=Widget(
                    name="mortgage_widget",
                    type="mortgage_widget",
                    order=1,
                    layout="vertical",
                    fields=["mortgage_data", "language"],
                ),
                args={
                    "mortgage_data": MortgageData.model_validate(mortgage_data),
                    "language": language,
                },
            ),
        }
        if context.llm_output != "":
            text_builder, text_input = self.make_text_input(context.llm_output)
            output[text_builder] = text_input
        return output


calculate_mortgage = CalculateMortgage()

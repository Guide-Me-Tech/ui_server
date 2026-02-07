from typing import Any, Dict, List
import json

import pydivkit as dk
from pydivkit.core import Expr


BooleanVariable = dk.BooleanVariable
IntegerVariable = dk.IntegerVariable
StringVariable = dk.StringVariable
DivAction = dk.DivAction
DivBorder = dk.DivBorder
DivCircleShape = dk.DivCircleShape
DivContainer = dk.DivContainer
DivContainerOrientation = dk.DivContainerOrientation
DivEdgeInsets = dk.DivEdgeInsets
DivFixedSize = dk.DivFixedSize
DivIndicator = dk.DivIndicator
DivMatchParentSize = dk.DivMatchParentSize
DivSolidBackground = dk.DivSolidBackground
DivStroke = dk.DivStroke
DivStrokeStyleDashed = dk.DivStrokeStyleDashed
DivText = dk.DivText
DivTimer = dk.DivTimer
DivWrapContentSize = dk.DivWrapContentSize


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TOTAL_STEPS = 8
POLL_INTERVAL_MS = 2000  # poll every 2 seconds
POLL_DURATION_MS = 120_000  # keep polling for up to 2 minutes
MESSAGES_ENDPOINT = "http://10.212.134.3:8003/new_messages"


def _make_action(log_id: str, url: str) -> DivAction:
    return DivAction(log_id=log_id, url=url)


# ---------------------------------------------------------------------------
# Variables  (8 steps)
# ---------------------------------------------------------------------------
def _build_variables() -> List[dk.DivVariable]:
    variables: List[dk.DivVariable] = [
        BooleanVariable(name="is_running", value=False),
        IntegerVariable(name="current_step", value=0),
        StringVariable(name="status_text", value="Idle"),
    ]
    for i in range(1, TOTAL_STEPS + 1):
        variables.append(BooleanVariable(name=f"step_{i}_visible", value=False))
        variables.append(StringVariable(name=f"step_{i}_text", value=""))
    variables.extend(
        [
            StringVariable(name="result_text", value=""),
            BooleanVariable(name="show_result", value=False),
        ]
    )
    return variables


# ---------------------------------------------------------------------------
# Timers – single polling timer that fetches from the backend
# ---------------------------------------------------------------------------
def _build_timers() -> List[DivTimer]:
    """Return a polling timer that hits the backend for new messages."""
    return [
        DivTimer(
            id="poll_timer",
            duration=POLL_DURATION_MS,
            tick_interval=POLL_INTERVAL_MS,
            tick_actions=[
                _make_action(
                    "poll_messages",
                    MESSAGES_ENDPOINT,
                ),
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# Reusable step row
# ---------------------------------------------------------------------------
def _make_step_container(
    step_number: int,
    visible_var: str,
    text_var: str,
    margin_bottom: int | None = 8,
) -> DivContainer:
    return DivContainer(
        orientation=DivContainerOrientation.HORIZONTAL,
        width=DivMatchParentSize(),
        background=[DivSolidBackground(color="#1E293B")],
        border=DivBorder(
            corner_radius=8,
            stroke=DivStroke(color="#334155", width=1),
        ),
        paddings=DivEdgeInsets(left=12, right=12, top=10, bottom=10),
        margins=DivEdgeInsets(bottom=margin_bottom) if margin_bottom else None,
        visibility=Expr(f"@{{{visible_var} ? 'visible' : 'gone'}}"),
        items=[
            DivContainer(
                width=DivFixedSize(value=24),
                height=DivFixedSize(value=24),
                background=[DivSolidBackground(color="#1E293B")],
                border=DivBorder(
                    corner_radius=12,
                    stroke=DivStroke(color="#475569", width=1),
                ),
                items=[
                    DivText(
                        text=str(step_number),
                        font_size=12,
                        text_color="#CBD5E1",
                    )
                ],
            ),
            DivText(
                text=Expr(f"@{{{text_var}}}"),
                font_size=14,
                text_color="#F1F5F9",
                margins=DivEdgeInsets(left=12),
                width=DivMatchParentSize(),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
def _make_header() -> DivContainer:
    return DivContainer(
        orientation=DivContainerOrientation.VERTICAL,
        width=DivMatchParentSize(),
        margins=DivEdgeInsets(bottom=24),
        items=[
            DivText(
                text="Agent run progress",
                font_size=24,
                font_weight=dk.DivFontWeight.MEDIUM,
                text_color="#F8FAFC",
            ),
            DivText(
                text=(
                    "This page displays real-time progress of an AI agent. "
                    "Messages are fetched dynamically from the backend as the "
                    "agent works through its 8-step pipeline."
                ),
                font_size=14,
                text_color="#94A3B8",
                margins=DivEdgeInsets(top=8),
                max_lines=3,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Start / Reset buttons
# ---------------------------------------------------------------------------
def _make_buttons() -> DivContainer:
    start_actions = [
        _make_action(
            "start_agent",
            "div-action://set_variable?name=is_running&value=true",
        ),
        _make_action(
            "set_status_running",
            "div-action://set_variable?name=status_text&value=Running...",
        ),
        _make_action(
            "start_polling",
            "div-action://timer?id=poll_timer&action=start",
        ),
    ]

    reset_actions: List[DivAction] = [
        _make_action(
            "stop_polling",
            "div-action://timer?id=poll_timer&action=stop",
        ),
        _make_action(
            "reset_running",
            "div-action://set_variable?name=is_running&value=false",
        ),
        _make_action(
            "reset_status",
            "div-action://set_variable?name=status_text&value=Idle",
        ),
    ]
    for i in range(1, TOTAL_STEPS + 1):
        reset_actions.append(
            _make_action(
                f"reset_step{i}_vis",
                f"div-action://set_variable?name=step_{i}_visible&value=false",
            )
        )
        reset_actions.append(
            _make_action(
                f"reset_step{i}_text",
                f"div-action://set_variable?name=step_{i}_text&value=",
            )
        )
    reset_actions.extend(
        [
            _make_action(
                "reset_show_result",
                "div-action://set_variable?name=show_result&value=false",
            ),
            _make_action(
                "reset_result_text",
                "div-action://set_variable?name=result_text&value=",
            ),
        ]
    )

    return DivContainer(
        orientation=DivContainerOrientation.HORIZONTAL,
        width=DivMatchParentSize(),
        margins=DivEdgeInsets(bottom=24),
        items=[
            DivContainer(
                orientation=DivContainerOrientation.HORIZONTAL,
                width=DivWrapContentSize(),
                background=[DivSolidBackground(color="#10B981")],
                border=DivBorder(corner_radius=8),
                paddings=DivEdgeInsets(left=16, right=16, top=8, bottom=8),
                actions=start_actions,
                items=[
                    DivText(
                        text="▶ Start agent",
                        font_size=14,
                        font_weight=dk.DivFontWeight.MEDIUM,
                        text_color="#020617",
                    )
                ],
            ),
            DivContainer(
                orientation=DivContainerOrientation.HORIZONTAL,
                width=DivWrapContentSize(),
                background=[DivSolidBackground(color="#1E293B")],
                border=DivBorder(
                    corner_radius=8,
                    stroke=DivStroke(color="#334155", width=1),
                ),
                paddings=DivEdgeInsets(left=12, right=12, top=8, bottom=8),
                margins=DivEdgeInsets(left=8),
                actions=reset_actions,
                items=[
                    DivText(
                        text="🔄 Reset",
                        font_size=12,
                        text_color="#E2E8F0",
                    )
                ],
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Agent activity section  (8 step rows + empty-state placeholder)
# ---------------------------------------------------------------------------
def _make_agent_activity_section() -> DivContainer:
    header_row = DivContainer(
        orientation=DivContainerOrientation.HORIZONTAL,
        width=DivMatchParentSize(),
        margins=DivEdgeInsets(bottom=16),
        items=[
            DivText(
                text="🕐 Agent activity",
                font_size=14,
                font_weight=dk.DivFontWeight.MEDIUM,
                text_color="#E2E8F0",
                width=DivWrapContentSize(),
            ),
            DivContainer(
                width=DivMatchParentSize(),
                items=[
                    DivText(
                        text=Expr("@{status_text}"),
                        font_size=12,
                        text_color="#94A3B8",
                    )
                ],
            ),
        ],
    )

    # Build 8 step containers
    step_items: List[DivContainer] = []
    for i in range(1, TOTAL_STEPS + 1):
        mb = 8 if i < TOTAL_STEPS else None
        step_items.append(
            _make_step_container(i, f"step_{i}_visible", f"step_{i}_text", mb)
        )

    # Empty-state placeholder (shown when no steps are visible yet)
    empty_state = DivContainer(
        orientation=DivContainerOrientation.HORIZONTAL,
        width=DivMatchParentSize(),
        background=[DivSolidBackground(color="#020617")],
        border=DivBorder(
            corner_radius=8,
            stroke=DivStroke(
                color="#1E293B",
                width=1,
                style=DivStrokeStyleDashed(),
            ),
        ),
        paddings=DivEdgeInsets(left=16, right=16, top=12, bottom=12),
        visibility=Expr("@{step_1_visible ? 'gone' : 'visible'}"),
        items=[
            DivIndicator(
                width=DivFixedSize(value=14),
                height=DivFixedSize(value=14),
                active_item_color="#38BDF8",
                inactive_item_color="#475569",
                shape=DivCircleShape(),
                minimum_item_size=0.4,
                active_item_size=1.0,
                visibility=Expr("@{is_running ? 'visible' : 'gone'}"),
            ),
            DivText(
                text="Waiting for the agent to report its first step…",
                font_size=12,
                text_color="#64748B",
                margins=DivEdgeInsets(left=8),
                visibility=Expr("@{is_running ? 'visible' : 'gone'}"),
            ),
            DivText(
                text=(
                    "Start the agent to see progress messages appear "
                    "here as they come in."
                ),
                font_size=12,
                text_color="#64748B",
                visibility=Expr("@{is_running ? 'gone' : 'visible'}"),
            ),
        ],
    )
    step_items.append(empty_state)

    steps_list = DivContainer(
        orientation=DivContainerOrientation.VERTICAL,
        width=DivMatchParentSize(),
        items=step_items,
    )

    return DivContainer(
        orientation=DivContainerOrientation.VERTICAL,
        width=DivMatchParentSize(),
        background=[DivSolidBackground(color="#0F172A")],
        border=DivBorder(
            corner_radius=12,
            stroke=DivStroke(color="#1E293B", width=1),
        ),
        paddings=DivEdgeInsets(left=20, right=20, top=20, bottom=20),
        margins=DivEdgeInsets(bottom=24),
        items=[header_row, steps_list],
    )


# ---------------------------------------------------------------------------
# Agent output section
# ---------------------------------------------------------------------------
def _make_agent_output_section() -> DivContainer:
    running_row = DivContainer(
        orientation=DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{is_running ? 'visible' : 'gone'}"),
        items=[
            DivIndicator(
                width=DivFixedSize(value=16),
                height=DivFixedSize(value=16),
                active_item_color="#4ADE80",
                inactive_item_color="#475569",
                shape=DivCircleShape(),
            ),
            DivText(
                text="Agent is still working on the answer…",
                font_size=14,
                text_color="#94A3B8",
                margins=DivEdgeInsets(left=8),
            ),
        ],
    )
    idle_text = DivText(
        text='Click "Start agent" to see the simulated progress and final result here.',
        font_size=14,
        text_color="#64748B",
        visibility=Expr("@{is_running || show_result ? 'gone' : 'visible'}"),
    )
    result_row = DivContainer(
        orientation=DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{show_result ? 'visible' : 'gone'}"),
        items=[
            DivText(
                text="✓",
                font_size=16,
                text_color="#10B981",
            ),
            DivText(
                text=Expr("@{result_text}"),
                font_size=14,
                text_color="#CBD5E1",
                margins=DivEdgeInsets(left=8),
            ),
        ],
    )
    return DivContainer(
        orientation=DivContainerOrientation.VERTICAL,
        width=DivMatchParentSize(),
        items=[running_row, idle_text, result_row],
    )


# ---------------------------------------------------------------------------
# Card builder
# ---------------------------------------------------------------------------
def build_agent_progress_card() -> Dict[str, Any]:
    """Build DivKit card with 8-step agent progress that polls the backend."""
    root = DivContainer(
        orientation=DivContainerOrientation.VERTICAL,
        width=DivMatchParentSize(),
        height=DivWrapContentSize(),
        background=[DivSolidBackground(color="#020617")],
        paddings=DivEdgeInsets(left=24, right=24, top=24, bottom=24),
        items=[
            _make_header(),
            _make_buttons(),
            _make_agent_activity_section(),
            _make_agent_output_section(),
        ],
    )

    card: Dict[str, Any] = {
        "card": {
            "log_id": "agent_progress",
            "variables": [v.dict() for v in _build_variables()],
            "states": [
                {
                    "state_id": 0,
                    "div": root.dict(),
                },
            ],
            "timers": [timer.dict() for timer in _build_timers()],
        }
    }

    # Patch indicator items_count for the empty-state indicator.
    activity_container = card["card"]["states"][0]["div"]["items"][2]
    empty_state = activity_container["items"][1]["items"][-1]
    empty_indicator = empty_state["items"][0]
    empty_indicator["items_count"] = TOTAL_STEPS

    return card


# ---------------------------------------------------------------------------
# Helper: build a step-row dict (used by the /new_messages endpoint to
# create DivKit patches without importing pydivkit on every request).
# ---------------------------------------------------------------------------
def make_step_row_dict(step_number: int, text: str) -> Dict[str, Any]:
    """Return a raw DivKit JSON dict for a single visible step row."""
    return {
        "type": "container",
        "orientation": "horizontal",
        "width": {"type": "match_parent"},
        "background": [{"type": "solid", "color": "#1E293B"}],
        "border": {
            "corner_radius": 8,
            "stroke": {"color": "#334155", "width": 1.0},
        },
        "paddings": {"left": 12, "right": 12, "top": 10, "bottom": 10},
        "margins": {"bottom": 8} if step_number < TOTAL_STEPS else None,
        "visibility": "visible",
        "items": [
            {
                "type": "container",
                "width": {"type": "fixed", "value": 24},
                "height": {"type": "fixed", "value": 24},
                "background": [{"type": "solid", "color": "#1E293B"}],
                "border": {
                    "corner_radius": 12,
                    "stroke": {"color": "#475569", "width": 1.0},
                },
                "items": [
                    {
                        "type": "text",
                        "text": str(step_number),
                        "font_size": 12,
                        "text_color": "#CBD5E1",
                    }
                ],
            },
            {
                "type": "text",
                "text": text,
                "font_size": 14,
                "text_color": "#F1F5F9",
                "margins": {"left": 12},
                "width": {"type": "match_parent"},
            },
        ],
    }


def save_agent_progress(path: str = "agent_progress.json") -> None:
    """Save the built card to JSON file."""
    card = build_agent_progress_card()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    save_agent_progress()

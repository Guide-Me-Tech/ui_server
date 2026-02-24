"""
Test script for Android - Button that checks monitor status.
Creates a pydivkit button that sends a request to https://smarty.smartbank.uz/monitor
and displays the response status.
"""

import json
import pydivkit as dv
from pydivkit.core import Expr


def create_monitor_check_button():
    """
    Create a button that sends a GET request to the monitor endpoint
    and displays success/error status based on the response.
    """
    prefix = "monitor"
    container_id = "monitor-check-container"

    # Status text variable to show response
    status_var = f"{prefix}_status_text"
    success_var = f"{prefix}_success_visible"
    error_var = f"{prefix}_error_visible"
    loading_var = f"{prefix}_loading_visible"
    button_var = f"{prefix}_button_visible"

    # Button with submit action
    check_button = dv.DivText(
        text="Check Monitor Status",
        font_size=16,
        font_weight=dv.DivFontWeight.MEDIUM,
        text_color="#FFFFFF",
        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
        background=[dv.DivSolidBackground(color="#2563EB")],
        border=dv.DivBorder(corner_radius=12),
        height=dv.DivFixedSize(value=48),
        width=dv.DivMatchParentSize(),
        paddings=dv.DivEdgeInsets(left=16, right=16, top=12, bottom=12),
        margins=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=8),
        visibility=Expr(f"@{{{button_var} == 1 ? 'visible' : 'gone'}}"),
        actions=[
            # Hide button on press
            dv.DivAction(
                log_id="monitor-hide-button",
                url=f"div-action://set_variable?name={button_var}&value=0",
            ),
            # Show loading state
            dv.DivAction(
                log_id="monitor-show-loading",
                url=f"div-action://set_variable?name={loading_var}&value=1",
            ),
            dv.DivAction(
                log_id="monitor-hide-success",
                url=f"div-action://set_variable?name={success_var}&value=0",
            ),
            dv.DivAction(
                log_id="monitor-hide-error",
                url=f"div-action://set_variable?name={error_var}&value=0",
            ),
            # Submit action with request
            dv.DivAction(
                log_id="monitor-check-request",
                url="divkit://send-request",
                typed=dv.DivActionSubmit(
                    container_id=container_id,
                    request=dv.DivActionSubmitRequest(
                        url="https://smarty.smartbank.uz/monitor",
                        method=dv.RequestMethod.GET,
                    ),
                    on_success_actions=[
                        dv.DivAction(
                            log_id="monitor-success-show",
                            url=f"div-action://set_variable?name={success_var}&value=1",
                        ),
                        dv.DivAction(
                            log_id="monitor-hide-loading-success",
                            url=f"div-action://set_variable?name={loading_var}&value=0",
                        ),
                        dv.DivAction(
                            log_id="monitor-hide-error-on-success",
                            url=f"div-action://set_variable?name={error_var}&value=0",
                        ),
                        dv.DivAction(
                            log_id="monitor-set-status-success",
                            url=f"div-action://set_variable?name={status_var}&value=Service is UP (200 OK)",
                        ),
                        # Keep button hidden on success
                    ],
                    on_fail_actions=[
                        dv.DivAction(
                            log_id="monitor-error-show",
                            url=f"div-action://set_variable?name={error_var}&value=1",
                        ),
                        dv.DivAction(
                            log_id="monitor-hide-loading-error",
                            url=f"div-action://set_variable?name={loading_var}&value=0",
                        ),
                        dv.DivAction(
                            log_id="monitor-hide-success-on-error",
                            url=f"div-action://set_variable?name={success_var}&value=0",
                        ),
                        dv.DivAction(
                            log_id="monitor-set-status-error",
                            url=f"div-action://set_variable?name={status_var}&value=Service is DOWN or unreachable",
                        ),
                        # Show button again on failure so user can retry
                        dv.DivAction(
                            log_id="monitor-show-button-on-error",
                            url=f"div-action://set_variable?name={button_var}&value=1",
                        ),
                    ],
                ),
            ),
        ],
    )

    # Loading indicator
    loading_container = dv.DivContainer(
        id="loading-indicator",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(f"@{{{loading_var} == 1 ? 'visible' : 'gone'}}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, left=16, right=16, bottom=8),
        paddings=dv.DivEdgeInsets(top=12, bottom=12, left=14, right=14),
        background=[dv.DivSolidBackground(color="#F3F4F6")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#D1D5DB", width=1)
        ),
        items=[
            dv.DivText(
                text="⏳",
                font_size=16,
                margins=dv.DivEdgeInsets(right=10),
            ),
            dv.DivText(
                text="Checking monitor status...",
                font_size=14,
                text_color="#4B5563",
                font_weight=dv.DivFontWeight.MEDIUM,
            ),
        ],
    )

    # Success container
    success_container = dv.DivContainer(
        id="success-container",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(f"@{{{success_var} == 1 ? 'visible' : 'gone'}}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, left=16, right=16, bottom=8),
        paddings=dv.DivEdgeInsets(top=12, bottom=12, left=14, right=14),
        background=[dv.DivSolidBackground(color="#ECFDF5")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        ),
        items=[
            dv.DivText(
                text="✅",
                font_size=16,
                margins=dv.DivEdgeInsets(right=10),
            ),
            dv.DivText(
                text=Expr(f"@{{{status_var}}}"),
                font_size=14,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=18,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=10, right=4),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-success",
                        url=f"div-action://set_variable?name={success_var}&value=0",
                    )
                ],
            ),
        ],
    )

    # Error container
    error_container = dv.DivContainer(
        id="error-container",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(f"@{{{error_var} == 1 ? 'visible' : 'gone'}}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, left=16, right=16, bottom=8),
        paddings=dv.DivEdgeInsets(top=12, bottom=12, left=14, right=14),
        background=[dv.DivSolidBackground(color="#FEF2F2")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#FECACA", width=1)
        ),
        items=[
            dv.DivText(
                text="❌",
                font_size=16,
                margins=dv.DivEdgeInsets(right=10),
            ),
            dv.DivText(
                text=Expr(f"@{{{status_var}}}"),
                font_size=14,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=18,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=10, right=4),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-error",
                        url=f"div-action://set_variable?name={error_var}&value=0",
                    )
                ],
            ),
        ],
    )

    # Title
    title = dv.DivText(
        text="Monitor Status Checker",
        font_size=20,
        font_weight=dv.DivFontWeight.BOLD,
        text_color="#1F2937",
        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        margins=dv.DivEdgeInsets(top=24, bottom=8, left=16, right=16),
    )

    # Subtitle
    subtitle = dv.DivText(
        text="Tap the button to check smarty.smartbank.uz/monitor",
        font_size=14,
        text_color="#6B7280",
        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        margins=dv.DivEdgeInsets(bottom=16, left=16, right=16),
    )

    # Main container
    main_container = dv.DivContainer(
        id=container_id,
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        variables=[
            dv.IntegerVariable(name=success_var, value=0),
            dv.IntegerVariable(name=error_var, value=0),
            dv.IntegerVariable(name=loading_var, value=0),
            dv.StringVariable(name=status_var, value=""),
            dv.IntegerVariable(name=button_var, value=1),  # Button visible by default
        ],
        items=[
            title,
            subtitle,
            check_button,
            loading_container,
            success_container,
            error_container,
        ],
    )

    return main_container


def create_login_button():
    """
    Create a button that sends a POST request to the login endpoint
    with username/password payload and displays success/error status.
    """
    prefix = "login"
    container_id = "login-container"
    
    # Separate variables for login button (prefixed with "login_")
    status_var = f"{prefix}_status_text"
    success_var = f"{prefix}_success_visible"
    error_var = f"{prefix}_error_visible"
    loading_var = f"{prefix}_loading_visible"
    button_var = f"{prefix}_button_visible"
    
    # Payload variables - these will be sent as the request body
    username_var = "username"
    password_var = "password"
    
    # Login button with POST submit action
    login_button = dv.DivText(
        text="Login to API",
        font_size=16,
        font_weight=dv.DivFontWeight.MEDIUM,
        text_color="#FFFFFF",
        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
        background=[dv.DivSolidBackground(color="#10B981")],
        border=dv.DivBorder(corner_radius=12),
        height=dv.DivFixedSize(value=48),
        width=dv.DivMatchParentSize(),
        paddings=dv.DivEdgeInsets(left=16, right=16, top=12, bottom=12),
        margins=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=8),
        visibility=Expr(f"@{{{button_var} == 1 ? 'visible' : 'gone'}}"),
        actions=[
            # Hide button on press
            dv.DivAction(
                log_id="login-hide-button",
                url=f"div-action://set_variable?name={button_var}&value=0",
            ),
            # Show loading state
            dv.DivAction(
                log_id="login-show-loading",
                url=f"div-action://set_variable?name={loading_var}&value=1",
            ),
            dv.DivAction(
                log_id="login-hide-success",
                url=f"div-action://set_variable?name={success_var}&value=0",
            ),
            dv.DivAction(
                log_id="login-hide-error",
                url=f"div-action://set_variable?name={error_var}&value=0",
            ),
            # Submit action with POST request - uses container variables as payload
            dv.DivAction(
                log_id="login-request",
                url="divkit://send-request",
                typed=dv.DivActionSubmit(
                    container_id=container_id,
                    request=dv.DivActionSubmitRequest(
                        url="https://api.g4h.uz/auth/login",
                        method=dv.RequestMethod.POST,
                        headers=[
                            dv.RequestHeader(name="Content-Type", value="application/json"),
                        ],
                    ),
                    on_success_actions=[
                        dv.DivAction(
                            log_id="login-success-show",
                            url=f"div-action://set_variable?name={success_var}&value=1",
                        ),
                        dv.DivAction(
                            log_id="login-hide-loading-success",
                            url=f"div-action://set_variable?name={loading_var}&value=0",
                        ),
                        dv.DivAction(
                            log_id="login-hide-error-on-success",
                            url=f"div-action://set_variable?name={error_var}&value=0",
                        ),
                        dv.DivAction(
                            log_id="login-set-status-success",
                            url=f"div-action://set_variable?name={status_var}&value=Login successful!",
                        ),
                        # Keep button hidden on success
                    ],
                    on_fail_actions=[
                        dv.DivAction(
                            log_id="login-error-show",
                            url=f"div-action://set_variable?name={error_var}&value=1",
                        ),
                        dv.DivAction(
                            log_id="login-hide-loading-error",
                            url=f"div-action://set_variable?name={loading_var}&value=0",
                        ),
                        dv.DivAction(
                            log_id="login-hide-success-on-error",
                            url=f"div-action://set_variable?name={success_var}&value=0",
                        ),
                        dv.DivAction(
                            log_id="login-set-status-error",
                            url=f"div-action://set_variable?name={status_var}&value=Login failed - check credentials",
                        ),
                        # Show button again on failure so user can retry
                        dv.DivAction(
                            log_id="login-show-button-on-error",
                            url=f"div-action://set_variable?name={button_var}&value=1",
                        ),
                    ],
                ),
            ),
        ],
    )
    
    # Loading indicator
    loading_container = dv.DivContainer(
        id="login-loading-indicator",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(f"@{{{loading_var} == 1 ? 'visible' : 'gone'}}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, left=16, right=16, bottom=8),
        paddings=dv.DivEdgeInsets(top=12, bottom=12, left=14, right=14),
        background=[dv.DivSolidBackground(color="#F3F4F6")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#D1D5DB", width=1)
        ),
        items=[
            dv.DivText(
                text="⏳",
                font_size=16,
                margins=dv.DivEdgeInsets(right=10),
            ),
            dv.DivText(
                text="Logging in...",
                font_size=14,
                text_color="#4B5563",
                font_weight=dv.DivFontWeight.MEDIUM,
            ),
        ],
    )
    
    # Success container
    success_container = dv.DivContainer(
        id="login-success-container",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(f"@{{{success_var} == 1 ? 'visible' : 'gone'}}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, left=16, right=16, bottom=8),
        paddings=dv.DivEdgeInsets(top=12, bottom=12, left=14, right=14),
        background=[dv.DivSolidBackground(color="#ECFDF5")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        ),
        items=[
            dv.DivText(
                text="✅",
                font_size=16,
                margins=dv.DivEdgeInsets(right=10),
            ),
            dv.DivText(
                text=Expr(f"@{{{status_var}}}"),
                font_size=14,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=18,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=10, right=4),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-login-success",
                        url=f"div-action://set_variable?name={success_var}&value=0",
                    )
                ],
            ),
        ],
    )
    
    # Error container
    error_container = dv.DivContainer(
        id="login-error-container",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(f"@{{{error_var} == 1 ? 'visible' : 'gone'}}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, left=16, right=16, bottom=8),
        paddings=dv.DivEdgeInsets(top=12, bottom=12, left=14, right=14),
        background=[dv.DivSolidBackground(color="#FEF2F2")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#FECACA", width=1)
        ),
        items=[
            dv.DivText(
                text="❌",
                font_size=16,
                margins=dv.DivEdgeInsets(right=10),
            ),
            dv.DivText(
                text=Expr(f"@{{{status_var}}}"),
                font_size=14,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=18,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=10, right=4),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-login-error",
                        url=f"div-action://set_variable?name={error_var}&value=0",
                    )
                ],
            ),
        ],
    )
    
    # Title
    title = dv.DivText(
        text="Login Test",
        font_size=20,
        font_weight=dv.DivFontWeight.BOLD,
        text_color="#1F2937",
        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        margins=dv.DivEdgeInsets(top=24, bottom=8, left=16, right=16),
    )
    
    # Subtitle
    subtitle = dv.DivText(
        text="POST to api.g4h.uz/auth/login",
        font_size=14,
        text_color="#6B7280",
        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        margins=dv.DivEdgeInsets(bottom=16, left=16, right=16),
    )
    
    # Login section container with its own variables
    # username and password variables will be used as the POST request payload
    login_container = dv.DivContainer(
        id=container_id,
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(),
        variables=[
            dv.IntegerVariable(name=success_var, value=0),
            dv.IntegerVariable(name=error_var, value=0),
            dv.IntegerVariable(name=loading_var, value=0),
            dv.StringVariable(name=status_var, value=""),
            dv.IntegerVariable(name=button_var, value=1),  # Button visible by default
            # Payload variables for the POST request
            dv.StringVariable(name=username_var, value="aslon"),
            dv.StringVariable(name=password_var, value="aslon"),
        ],
        items=[
            title,
            subtitle,
            login_button,
            loading_container,
            success_container,
            error_container,
        ],
    )
    
    return login_container


def create_combined_ui():
    """
    Create a combined UI with both monitor check and login buttons,
    each with their own separate variables.
    """
    monitor_section = create_monitor_check_button()
    login_section = create_login_button()
    
    # Separator
    separator = dv.DivSeparator(
        delimiter_style=dv.DivSeparatorDelimiterStyle(color="#E5E7EB"),
        margins=dv.DivEdgeInsets(top=24, bottom=8, left=16, right=16),
    )
    
    # Main container combining both sections
    main_container = dv.DivContainer(
        id="main-container",
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        items=[
            monitor_section,
            separator,
            login_section,
        ],
    )
    
    return dv.make_div(main_container)


if __name__ == "__main__":
    div_json = create_combined_ui()

    # Print to console
    print(json.dumps(div_json, indent=2, ensure_ascii=False))

    # Save to file
    with open("logs/json/monitor_check_button.json", "w") as f:
        json.dump(div_json, f, indent=2, ensure_ascii=False)

    print("\n✅ DivKit JSON saved to logs/json/monitor_check_button.json")

"""
Action Helpers - Utilities for creating pydivkit actions with on_success and on_failure handlers.

This module provides consistent patterns for:
1. Creating actions with success/error feedback
2. Building feedback containers (success/error UI elements)
3. Managing feedback state variables
"""

import pydivkit as dv
from pydivkit.core import Expr
from typing import Optional, List, Dict, Any
from .const_values import LanguageOptions


# ============================================================================
# Feedback Text Maps (Localized)
# ============================================================================

FEEDBACK_TEXTS = {
    LanguageOptions.RUSSIAN: {
        "success_default": "Операция выполнена успешно!",
        "error_default": "Произошла ошибка. Попробуйте еще раз.",
        "added_to_cart": "Товар добавлен в корзину!",
        "cart_error": "Не удалось добавить товар в корзину",
        "payment_success": "Платеж выполнен успешно!",
        "payment_error": "Ошибка платежа. Попробуйте еще раз.",
        "action_approved": "Действие подтверждено!",
        "action_rejected": "Действие отклонено",
        "action_error": "Не удалось выполнить действие",
        "contact_selected": "Контакт выбран",
        "category_selected": "Категория выбрана",
        "card_selected": "Карта выбрана",
        "loading": "Загрузка...",
        "retry": "Повторить",
        "dismiss": "Закрыть",
    },
    LanguageOptions.ENGLISH: {
        "success_default": "Operation completed successfully!",
        "error_default": "An error occurred. Please try again.",
        "added_to_cart": "Item added to cart!",
        "cart_error": "Failed to add item to cart",
        "payment_success": "Payment completed successfully!",
        "payment_error": "Payment failed. Please try again.",
        "action_approved": "Action approved!",
        "action_rejected": "Action rejected",
        "action_error": "Failed to perform action",
        "contact_selected": "Contact selected",
        "category_selected": "Category selected",
        "card_selected": "Card selected",
        "loading": "Loading...",
        "retry": "Retry",
        "dismiss": "Dismiss",
    },
    LanguageOptions.UZBEK: {
        "success_default": "Amal muvaffaqiyatli bajarildi!",
        "error_default": "Xatolik yuz berdi. Qayta urinib ko'ring.",
        "added_to_cart": "Mahsulot savatga qo'shildi!",
        "cart_error": "Mahsulotni savatga qo'shib bo'lmadi",
        "payment_success": "To'lov muvaffaqiyatli amalga oshirildi!",
        "payment_error": "To'lov xatosi. Qayta urinib ko'ring.",
        "action_approved": "Harakat tasdiqlandi!",
        "action_rejected": "Harakat rad etildi",
        "action_error": "Harakatni bajarib bo'lmadi",
        "contact_selected": "Kontakt tanlandi",
        "category_selected": "Kategoriya tanlandi",
        "card_selected": "Karta tanlandi",
        "loading": "Yuklanmoqda...",
        "retry": "Qayta urinish",
        "dismiss": "Yopish",
    },
}


# ============================================================================
# Feedback State Variables
# ============================================================================

def create_feedback_variables(prefix: str = "") -> List[dv.DivVariable]:
    """
    Create standard feedback state variables for a container.
    
    Args:
        prefix: Optional prefix for variable names to avoid conflicts
        
    Returns:
        List of DivVariable objects for success/error state management
    """
    var_prefix = f"{prefix}_" if prefix else ""
    return [
        dv.IntegerVariable(name=f"{var_prefix}success_visible", value=0),
        dv.IntegerVariable(name=f"{var_prefix}error_visible", value=0),
        dv.IntegerVariable(name=f"{var_prefix}loading_visible", value=0),
        dv.StringVariable(name=f"{var_prefix}success_text", value=""),
        dv.StringVariable(name=f"{var_prefix}error_text", value=""),
    ]


# ============================================================================
# Success/Error Actions Builders
# ============================================================================

def create_success_actions(
    log_id: str,
    success_text: str = "",
    prefix: str = "",
    additional_actions: Optional[List[dv.DivAction]] = None,
) -> List[dv.DivAction]:
    """
    Create standard success actions that show success feedback.
    
    Args:
        log_id: Log identifier for the action
        success_text: Text to display on success
        prefix: Variable name prefix
        additional_actions: Additional actions to include
        
    Returns:
        List of DivAction objects for success handling
    """
    var_prefix = f"{prefix}_" if prefix else ""
    actions = [
        dv.DivAction(
            log_id=f"{log_id}-success-show",
            url=f"div-action://set_variable?name={var_prefix}success_visible&value=1",
        ),
        dv.DivAction(
            log_id=f"{log_id}-hide-error",
            url=f"div-action://set_variable?name={var_prefix}error_visible&value=0",
        ),
        dv.DivAction(
            log_id=f"{log_id}-hide-loading",
            url=f"div-action://set_variable?name={var_prefix}loading_visible&value=0",
        ),
    ]
    
    if success_text:
        actions.append(
            dv.DivAction(
                log_id=f"{log_id}-set-success-text",
                url=f"div-action://set_variable?name={var_prefix}success_text&value={success_text}",
            )
        )
    
    if additional_actions:
        actions.extend(additional_actions)
    
    return actions


def create_failure_actions(
    log_id: str,
    error_text: str = "",
    prefix: str = "",
    additional_actions: Optional[List[dv.DivAction]] = None,
) -> List[dv.DivAction]:
    """
    Create standard failure actions that show error feedback.
    
    Args:
        log_id: Log identifier for the action
        error_text: Text to display on error
        prefix: Variable name prefix
        additional_actions: Additional actions to include
        
    Returns:
        List of DivAction objects for failure handling
    """
    var_prefix = f"{prefix}_" if prefix else ""
    actions = [
        dv.DivAction(
            log_id=f"{log_id}-error-show",
            url=f"div-action://set_variable?name={var_prefix}error_visible&value=1",
        ),
        dv.DivAction(
            log_id=f"{log_id}-hide-success",
            url=f"div-action://set_variable?name={var_prefix}success_visible&value=0",
        ),
        dv.DivAction(
            log_id=f"{log_id}-hide-loading",
            url=f"div-action://set_variable?name={var_prefix}loading_visible&value=0",
        ),
    ]
    
    if error_text:
        actions.append(
            dv.DivAction(
                log_id=f"{log_id}-set-error-text",
                url=f"div-action://set_variable?name={var_prefix}error_text&value={error_text}",
            )
        )
    
    if additional_actions:
        actions.extend(additional_actions)
    
    return actions


def create_loading_actions(
    log_id: str,
    prefix: str = "",
) -> List[dv.DivAction]:
    """
    Create actions to show loading state.
    
    Args:
        log_id: Log identifier for the action
        prefix: Variable name prefix
        
    Returns:
        List of DivAction objects for loading state
    """
    var_prefix = f"{prefix}_" if prefix else ""
    return [
        dv.DivAction(
            log_id=f"{log_id}-show-loading",
            url=f"div-action://set_variable?name={var_prefix}loading_visible&value=1",
        ),
        dv.DivAction(
            log_id=f"{log_id}-hide-success",
            url=f"div-action://set_variable?name={var_prefix}success_visible&value=0",
        ),
        dv.DivAction(
            log_id=f"{log_id}-hide-error",
            url=f"div-action://set_variable?name={var_prefix}error_visible&value=0",
        ),
    ]


# ============================================================================
# Feedback Container Builders
# ============================================================================

def create_success_container(
    container_id: str = "success-container",
    prefix: str = "",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
    custom_text: Optional[str] = None,
) -> dv.DivContainer:
    """
    Create a success feedback container with conditional visibility.
    
    Args:
        container_id: ID for the container
        prefix: Variable name prefix
        language: Language for localization
        custom_text: Custom success text (if None, uses variable)
        
    Returns:
        DivContainer configured for success feedback display
    """
    var_prefix = f"{prefix}_" if prefix else ""
    texts = FEEDBACK_TEXTS.get(language, FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    
    text_content = custom_text or f"@{{{var_prefix}success_text}}"
    if not custom_text:
        # Use default text if variable is empty
        text_content = texts["success_default"]
    
    return dv.DivContainer(
        id=container_id,
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(f"@{{{var_prefix}success_visible == 1 ? 'visible' : 'gone'}}"),
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
                text=text_content,
                font_size=14,
                font_family="Manrope",
                text_color="#065F46",
                font_weight=dv.DivFontWeight.MEDIUM,
                line_height=20,
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
                        log_id=f"dismiss-success-{container_id}",
                        url=f"div-action://set_variable?name={var_prefix}success_visible&value=0",
                    )
                ],
            ),
        ],
    )


def create_error_container(
    container_id: str = "error-container",
    prefix: str = "",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
    custom_text: Optional[str] = None,
) -> dv.DivContainer:
    """
    Create an error feedback container with conditional visibility.
    
    Args:
        container_id: ID for the container
        prefix: Variable name prefix
        language: Language for localization
        custom_text: Custom error text (if None, uses variable)
        
    Returns:
        DivContainer configured for error feedback display
    """
    var_prefix = f"{prefix}_" if prefix else ""
    texts = FEEDBACK_TEXTS.get(language, FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    
    text_expr = f"@{{{var_prefix}error_text}}" if not custom_text else custom_text
    
    return dv.DivContainer(
        id=container_id,
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(f"@{{{var_prefix}error_visible == 1 ? 'visible' : 'gone'}}"),
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
                text="⚠️",
                font_size=16,
                margins=dv.DivEdgeInsets(right=10),
            ),
            dv.DivText(
                text=text_expr,
                font_size=14,
                font_family="Manrope",
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.MEDIUM,
                line_height=20,
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
                        log_id=f"dismiss-error-{container_id}",
                        url=f"div-action://set_variable?name={var_prefix}error_visible&value=0",
                    )
                ],
            ),
        ],
    )


def create_loading_container(
    container_id: str = "loading-container",
    prefix: str = "",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> dv.DivContainer:
    """
    Create a loading indicator container with conditional visibility.
    
    Args:
        container_id: ID for the container
        prefix: Variable name prefix
        language: Language for localization
        
    Returns:
        DivContainer configured for loading state display
    """
    var_prefix = f"{prefix}_" if prefix else ""
    texts = FEEDBACK_TEXTS.get(language, FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    
    return dv.DivContainer(
        id=container_id,
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr(f"@{{{var_prefix}loading_visible == 1 ? 'visible' : 'gone'}}"),
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
                text=texts["loading"],
                font_size=14,
                font_family="Manrope",
                text_color="#4B5563",
                font_weight=dv.DivFontWeight.MEDIUM,
                line_height=20,
            ),
        ],
    )


# ============================================================================
# Complete Action Builders with Handlers
# ============================================================================

def create_submit_action_with_handlers(
    log_id: str,
    container_id: str,
    url: str,
    method: dv.RequestMethod = dv.RequestMethod.POST,
    headers: Optional[List[dv.RequestHeader]] = None,
    payload: Optional[Dict[str, Any]] = None,
    success_text: str = "",
    error_text: str = "",
    prefix: str = "",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
    additional_success_actions: Optional[List[dv.DivAction]] = None,
    additional_failure_actions: Optional[List[dv.DivAction]] = None,
) -> dv.DivAction:
    """
    Create a complete DivActionSubmit with on_success and on_fail handlers.
    
    Args:
        log_id: Log identifier for the action
        container_id: Container ID for the submit action
        url: Request URL
        method: HTTP method (default POST)
        headers: Optional request headers
        payload: Optional action payload
        success_text: Text to display on success
        error_text: Text to display on error
        prefix: Variable name prefix
        language: Language for localization
        additional_success_actions: Extra actions on success
        additional_failure_actions: Extra actions on failure
        
    Returns:
        DivAction configured with submit and handlers
    """
    texts = FEEDBACK_TEXTS.get(language, FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    
    final_success_text = success_text or texts["success_default"]
    final_error_text = error_text or texts["error_default"]
    
    action = dv.DivAction(
        log_id=log_id,
        url="divkit://send-request",
        payload=payload,
        typed=dv.DivActionSubmit(
            container_id=container_id,
            request=dv.DivActionSubmitRequest(
                url=url,
                method=method,
                headers=headers or [],
            ),
            on_success_actions=create_success_actions(
                log_id=log_id,
                success_text=final_success_text,
                prefix=prefix,
                additional_actions=additional_success_actions,
            ),
            on_fail_actions=create_failure_actions(
                log_id=log_id,
                error_text=final_error_text,
                prefix=prefix,
                additional_actions=additional_failure_actions,
            ),
        ),
    )
    
    return action


def create_simple_action_with_feedback(
    log_id: str,
    url: str,
    payload: Optional[Dict[str, Any]] = None,
    success_text: str = "",
    prefix: str = "",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> List[dv.DivAction]:
    """
    Create a simple action (URL navigation, state change) with success feedback.
    For actions that don't involve network requests but should show feedback.
    
    Args:
        log_id: Log identifier for the action
        url: Action URL
        payload: Optional action payload
        success_text: Text to display on success
        prefix: Variable name prefix
        language: Language for localization
        
    Returns:
        List of DivAction objects (main action + feedback actions)
    """
    texts = FEEDBACK_TEXTS.get(language, FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    final_success_text = success_text or texts["success_default"]
    
    actions = [
        dv.DivAction(
            log_id=log_id,
            url=url,
            payload=payload,
        ),
    ]
    
    # Add success feedback actions
    actions.extend(
        create_success_actions(
            log_id=log_id,
            success_text=final_success_text,
            prefix=prefix,
        )
    )
    
    return actions


def create_selection_action(
    log_id: str,
    url: str,
    payload: Dict[str, Any],
    success_text: str = "",
    prefix: str = "",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
    show_feedback: bool = True,
) -> List[dv.DivAction]:
    """
    Create a selection action (for cards, categories, suppliers, etc.) with optional feedback.
    
    Args:
        log_id: Log identifier for the action
        url: Action URL (typically divkit:// scheme)
        payload: Selection payload data
        success_text: Text to display on success
        prefix: Variable name prefix
        language: Language for localization
        show_feedback: Whether to show success feedback
        
    Returns:
        List of DivAction objects
    """
    actions = [
        dv.DivAction(
            log_id=log_id,
            url=url,
            payload=payload,
        ),
    ]
    
    if show_feedback:
        texts = FEEDBACK_TEXTS.get(language, FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
        final_success_text = success_text or texts["success_default"]
        
        actions.extend(
            create_success_actions(
                log_id=log_id,
                success_text=final_success_text,
                prefix=prefix,
            )
        )
    
    return actions


# ============================================================================
# Utility Functions
# ============================================================================

def get_feedback_text(
    key: str,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> str:
    """
    Get localized feedback text by key.
    
    Args:
        key: Text key (e.g., 'success_default', 'added_to_cart')
        language: Language for localization
        
    Returns:
        Localized text string
    """
    texts = FEEDBACK_TEXTS.get(language, FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    return texts.get(key, texts.get("success_default", ""))


def create_feedback_wrapper(
    content: dv.Div,
    prefix: str = "",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
    include_loading: bool = False,
) -> dv.DivContainer:
    """
    Wrap content with feedback containers (success, error, optionally loading).
    
    Args:
        content: The main content div
        prefix: Variable name prefix
        language: Language for localization
        include_loading: Whether to include loading indicator
        
    Returns:
        DivContainer with content and feedback containers
    """
    items = []
    
    # Add feedback containers at the top
    items.append(create_success_container(prefix=prefix, language=language))
    items.append(create_error_container(prefix=prefix, language=language))
    
    if include_loading:
        items.append(create_loading_container(prefix=prefix, language=language))
    
    # Add the main content
    items.append(content)
    
    return dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        items=items,
        variables=create_feedback_variables(prefix=prefix),
        width=dv.DivMatchParentSize(),
    )

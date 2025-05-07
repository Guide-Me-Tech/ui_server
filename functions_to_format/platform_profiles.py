import os
import sys
import logging
from typing import Dict, Any, List
from conf import logger

"""
- Different platforms (mobile, desktop, voice assistant, smart TV, car dashboard, AR/VR) may require different UI adjustments.
- By defining profiles and applying them dynamically, we adapt UI without modifying core logic.
- All configuration (which profiles to apply, in what order) is controlled via environment variables.
- Detailed logging for each step ensures easy debugging.

Key Environment Variables:
- PLATFORM_PROFILES_LIST: Comma-separated list of profiles to apply (e.g. "mobile,desktop,voice_assistant")
- PROFILE_LOG_LEVEL: Logging level for platform profile actions (default: ERROR)
- PROFILE_RESOURCE_SAVING_MODE: If true, minimize overhead in profile application.
- Each profile might have its own ENV configs for further customization.

Profiles we define (examples):
1. mobile:    Tailor UI for small screens, reduce image sizes, simplify layouts.
2. desktop:   Utilize larger displays, add advanced navigation widgets.
3. voice_assistant: Turn UI into voice-friendly structures, maybe remove visuals and keep text hints.
4. smart_tv:  Larger fonts, highlight remote navigation hints.
5. car_dashboard: Minimal distractions, large buttons, reduce text.
6. ar_vr:     UI optimized for AR/VR, maybe 3D structures or simplified overlays.

This is flexible and scenario-based. Logging steps as "Janis Rubins step X".
"""

# Janis Rubins step 1: Load environment vars
PROFILE_LOG_LEVEL = os.environ.get("PROFILE_LOG_LEVEL", "ERROR").upper()
PLATFORM_PROFILES_LIST = os.environ.get("PLATFORM_PROFILES_LIST", "")
PROFILE_RESOURCE_SAVING_MODE = (
    os.environ.get("PROFILE_RESOURCE_SAVING_MODE", "true").lower() == "true"
)


# Janis Rubins step 3: Base class for profiles
class PlatformProfile:
    """
    Abstract base profile:
    Each profile implements apply_profile(ui_data: dict) -> dict
    """

    def apply_profile(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("apply_profile must be implemented by subclasses")

    def log_application_start(self):
        logger.debug(f"Applying {self.__class__.__name__} profile.")


# Janis Rubins step 4: Define each profile class


class MobileProfile(PlatformProfile):
    """
    Janis Rubins step 5: MobileProfile
    - Adjust UI for small screens: reduce image sizes, maybe shorten text.
    - Example: for each 'ui' element, if it has 'image', reduce resolution.
    """

    def apply_profile(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log_application_start()
        if PROFILE_RESOURCE_SAVING_MODE:
            logger.debug(
                "MobileProfile: Resource saving mode on, minimal transformations."
            )
        ui_list = ui_data.get("ui", [])
        for element in ui_list:
            if "widget" in element and "image" in element.get("data", {}):
                # Reduce image size by changing a field (simulated)
                element["data"]["image_size"] = "small"
        return ui_data


class DesktopProfile(PlatformProfile):
    """
    Janis Rubins step 6: DesktopProfile
    - Larger displays: we can add navigation menus, more complex layouts.
    - Example: add a "sidebar" if not present.
    """

    def apply_profile(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log_application_start()
        if PROFILE_RESOURCE_SAVING_MODE:
            # minimal overhead: Just add a simple sidebar placeholder
            ui_data["sidebar"] = {
                "type": "nav_menu",
                "items": ["Home", "Settings", "Help"],
            }
        else:
            # If not resource saving, add more detailed menus
            ui_data["sidebar"] = {
                "type": "nav_menu",
                "items": ["Home", "Settings", "Help", "Advanced Options"],
            }
        return ui_data


class VoiceAssistantProfile(PlatformProfile):
    """
    Janis Rubins step 7: VoiceAssistantProfile
    - Voice friendly: remove visuals, keep text prompts short.
    - Example: For each UI element, if it has text, keep only essential text and remove images.
    """

    def apply_profile(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log_application_start()
        ui_list = ui_data.get("ui", [])
        for element in ui_list:
            # Remove visual fields if present
            if "data" in element:
                element["data"].pop("image", None)
                element["data"].pop("video", None)
            # Possibly shorten text if needed
            # If resource saving mode, skip complex text processing.
            if not PROFILE_RESOURCE_SAVING_MODE and "text" in element.get("data", {}):
                text = element["data"]["text"]
                if len(text) > 50:
                    element["data"]["text"] = text[:50] + "..."
        return ui_data


class SmartTVProfile(PlatformProfile):
    """
    Janis Rubins step 8: SmartTVProfile
    - Large fonts, highlight remote navigation cues.
    - Example: Add a field "tv_optimized"=True to help front-end know to increase fonts.
    """

    def apply_profile(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log_application_start()
        # Mark the whole UI as tv_optimized
        ui_data["tv_optimized"] = True
        # If resource saving mode: minimal changes
        if not PROFILE_RESOURCE_SAVING_MODE:
            # Possibly add navigation hints:
            ui_data["navigation_hints"] = "Use arrow keys to navigate, OK to select"
        return ui_data


class CarDashboardProfile(PlatformProfile):
    """
    Janis Rubins step 9: CarDashboardProfile
    - Minimal distractions, large buttons, reduce text.
    - Example: Make all text short, large buttons, remove complex layouts.
    """

    def apply_profile(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log_application_start()
        ui_list = ui_data.get("ui", [])
        for element in ui_list:
            # Remove long texts
            if "data" in element and "text" in element["data"]:
                text = element["data"]["text"]
                if len(text) > 20:
                    element["data"]["text"] = text[:20] + "..."
            # Assume making buttons larger
            element["data"]["button_size"] = "large_button"
        return ui_data


class ARVRProfile(PlatformProfile):
    """
    Janis Rubins step 10: ARVRProfile
    - UI adapted for AR/VR: maybe add depth info, simplify overlays.
    - Example: add a "depth" field to each element, remove complicated backgrounds.
    """

    def apply_profile(self, ui_data: Dict[str, Any]) -> Dict[str, Any]:
        self.log_application_start()
        ui_list = ui_data.get("ui", [])
        for i, element in enumerate(ui_list):
            element["ar_vr_depth"] = i * 0.5  # assign some depth increment
            # Remove backgrounds if resource mode is off we can do more complex
            if not PROFILE_RESOURCE_SAVING_MODE:
                element["data"].pop("background_pattern", None)
        return ui_data


# Janis Rubins step 11: Profile registry
# We define a map from profile name to class.
# If needed, can load dynamically or from ENV. For now, statically defined:
PROFILE_CLASSES = {
    "mobile": MobileProfile,
    "desktop": DesktopProfile,
    "voice_assistant": VoiceAssistantProfile,
    "smart_tv": SmartTVProfile,
    "car_dashboard": CarDashboardProfile,
    "ar_vr": ARVRProfile,
}


def apply_platform_profiles(ui_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Janis Rubins step 12: Main function to apply profiles.
    Reads PLATFORM_PROFILES_LIST and applies each profile in order.
    """
    logger.debug("Applying platform profiles...")
    if not PLATFORM_PROFILES_LIST.strip():
        # No profiles specified
        logger.debug("No platform profiles specified, returning UI data unchanged.")
        return ui_data

    profiles_to_apply = [
        p.strip() for p in PLATFORM_PROFILES_LIST.split(",") if p.strip()
    ]

    for profile_name in profiles_to_apply:
        profile_cls = PROFILE_CLASSES.get(profile_name)
        if profile_cls is None:
            logger.warning(f"No profile class found for '{profile_name}', skipping.")
            continue
        profile_instance = profile_cls()
        logger.debug(f"Applying profile: {profile_name}")
        ui_data = profile_instance.apply_profile(ui_data)
        logger.debug(f"Profile {profile_name} applied successfully.")

    logger.debug("All specified platform profiles applied.")
    return ui_data


# Janis Rubins step 13: Example usage (commented out)
# Suppose we have a ui_data from dynamic_ui_builder:
# ui_data = {"ui":[{"widget":"text_widget","data":{"text":"Hello World","image":"banner.png"}}]}
# os.environ["PLATFORM_PROFILES_LIST"]="mobile,car_dashboard"
# final_ui = apply_platform_profiles(ui_data)
# print(final_ui)

# With changes in environment variables, we can adapt this UI for different platforms without code changes.

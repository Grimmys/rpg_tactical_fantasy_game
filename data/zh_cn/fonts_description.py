from typing import Union

scale = 1

fonts_description: dict[str, dict[str, Union[str, int]]] = {
    "BUTTON_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(20 * scale),
    },
    "ITEM_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(18 * scale),
    },
    "ITEM_FONT_HOVER": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(19 * scale),
    },
    "ITEM_FONT_STRONG": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(10 * scale),
    },
    "MISSION_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(12 * scale),
    },
    "MENU_SUB_TITLE_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(22 * scale),
    },
    "ITEM_DESC_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(18 * scale),
    },
    "MENU_TITLE_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(26 * scale),
    },
    "SIDEBAR_TITLE_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(16 * scale),
    },
    "TITLE_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(46 * scale),
    },
    "LEVEL_TITLE_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": int(60 * scale),
    },
    "ITALIC_ITEM_FONT": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": 14,
    },
    "ITALIC_ITEM_FONT_HOVER": {
        "name": "fonts/fusion-pixel-12px-proportional-zh_hans.ttf",
        "size": 16,
    },
    "LANGUAGE_FONT": {"name": "fonts/Autonym.ttf", "size": 18},
    "FPS_FONT": {"default": True},
}

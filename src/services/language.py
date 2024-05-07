import os
import pathlib

from lxml import etree

# Get language from options.xml
language: str = etree.parse("saves/options.xml").find("language").text
DATA_PATH = "data/" + language + "/"

if language == "en":
    from data.en.fonts_description import fonts_description
    from data.en.text import *
elif language == "zh_cn":
    from data.zh_cn.fonts_description import fonts_description
    from data.zh_cn.text import *


def get_localized_string(tree: etree.Element):
    """
    Get string of the text in current language from etree element containing language name tags.
    If current language tag cannot be found, return English text.
    If the etree element doesn't contain any language tag, return the element's text.

    Arguments:
    tree -- etree element containing language name tags

    Returns:
    String of the text in current language
    """
    localized_string = tree.find(language)
    if localized_string is not None:
        return localized_string.text
    elif language != "en":
        english_text = tree.find("en")
        if english_text is not None:
            return english_text.text
    return tree.text

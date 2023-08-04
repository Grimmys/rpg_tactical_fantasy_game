import sys

from lxml import etree

language: str = etree.parse("saves/options.xml").find("language").text

# Surpported language names
STR_ENGLISH = "English"
STR_CHINESE_SIMP = "Chinese"

DATA_PATH = "data/" + language + "/"

if language == "en":
    from data.en.text import *
    from data.en.fonts_description import fonts_description
elif language == "zh_cn":
    from data.zh_cn.text import *
    from data.zh_cn.fonts_description import fonts_description


def get_languaged_text(tree: etree._Element):
    languaged_text = tree.find(language)
    if languaged_text is not None:
        return languaged_text.text
    elif language != "en":
        english_text = tree.find("en")
        if english_text is not None:
            return english_text.text
    return tree.text

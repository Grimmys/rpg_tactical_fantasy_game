from lxml import etree

# Get language from options.xml
language: str = etree.parse("saves/options.xml").find("language").text
DATA_PATH = "data/" + language + "/"

if language == "en":
    from data.en.text import *
    from data.en.fonts_description import fonts_description
elif language == "zh_cn":
    from data.zh_cn.text import *
    from data.zh_cn.fonts_description import fonts_description


def get_languaged_text(tree: etree._Element):
    """
    Get string of the text in current language from etree element containing language name tags.
    If cannot find current language tag, return English text.
    If the etree element doesn't contain any language tag, return the element's text.

    Arguments:
    tree -- etree element containing language name tags

    Returns:
    String of the text in current language
    """
    languaged_text = tree.find(language)
    if languaged_text is not None:
        return languaged_text.text
    elif language != "en":
        english_text = tree.find("en")
        if english_text is not None:
            return english_text.text
    return tree.text

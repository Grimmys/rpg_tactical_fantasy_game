language = "cn"
DATA_PATH = "data/" + language + "/"

if language == "en":
    from data.en.text import *
    from data.en.fonts_description import fonts_description
elif language == "cn":
    from data.cn.text import *
    from data.cn.fonts_description import fonts_description
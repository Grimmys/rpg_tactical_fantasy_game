[ [English 英文](#Introduction) | [Chinese 中文](#多语言支持说明) ]

# Multilingual Support Description

## Introduction
This update adds an interface for implementing multilingual functionality to the game. Due to the unfinished translation work, some content is temporarily missing, but it is harmless, the interface has been completed. I will continue to finish Chinese translation.

## How to add a new language
1. Create a language directory: Create a copy of the `en` folder under the `data` folder and rename it to the name of the language you need, assuming it is `language_name`. (Due to the unfinished translation work, some content is temporarily missing.)
2. Copy font files: Add the font files required for your language in ttf format under the `fonts` folder.
3. Import font files: Modify the contents of `data/language_name/fonts_description.py` and change the name of the font file to the name of the font file you need.
4. Add language button: Modify the content of the `element_grid` list in the `create_choose_language_menu` function in `menu_creater_manager.py`. Add a button with your language's full name as `title` and `language_name` as `callback`. For example:
   ```python
    element_grid = [
        [Button(title="English", callback=lambda: buttons_callback("en"))],
        [Button(title="中文简体", callback=lambda: buttons_callback("zh_cn"))],
        ...
        [Button(title="Language Full Name", callback=lambda: buttons_callback("language_name"))],
    ]
   ```
5. The content that needs to be translated includes:
    * Strings, function outputs, and dictionaries in `text.py`.
    * The content of each txt file under `data/language_name/maps/level_number`.
    * Some content in each map_properties.tmx file under `data/language_name/maps/level_number`, including:
        + The value of level_name.
        + The value of main_mission_description.
        + The value of limited_mission_description (if it exists).
    * Some content in some xml files under `data/language_name/`.
        + The content within the `<talk>` tag in `characters.xml`.
        + The content within the `<info>` tag in `alternations.xml`.
        + The content within the `<info>` tag in `items.xml`.
        + The content within the `<info>` and the `<name>` tags in `skills.xml`.
    Please note that the format of the above changes must be: `<language_name> translated content </language_name>`. For example:
        ```xml
        ...
        <interaction>
            <talk>
                <en> Hurry up ! Leave ... the necropolis. </en>
                <zh_cn> 快呀！从...进入墓地。</zh_cn>
            </talk>
            <talk>
                <en> The clock is ticking... original place. </en>
                <zh_cn> 时钟在滴答...回原来的地方。 </zh_cn>
            </talk>
        </interaction>
        ...
        ```

# Changes and Explanations
1. Created `src/gui/language.py` to handle language-related matters. `language.py` will import the corresponding `text.py` according to the language in `saves/options.xml`.
2. Moved all static strings involving output in all files to variables in `text.py`, with variable names composed of uppercase letters and underscores of English content of strings. If the last character of a variable name is an underscore, it means that there is a colon at the end of the string.
3. Moved all contents involving variables and output in all files to be processed as functions in `text.py`.
4. Corresponded all contents involving class names and output in all files with dictionaries in `text.py`. (The original processing method is temporarily retained for English)
5. Changed the method of reading `<info>` or `<talk>` tags from xml files under the `data` folder. Added `<language_name>` tag. (But still retained the original processing method because translation work has not been completed)
6. Added code related to restarting games in `main.py`. Used to restart games after adjusting languages. Since I couldn't find a better way to restart games, I used creating subprocesses to implement game restart functionality.
7. Changed return value type of variable passed to `quit_game` in each `Scene` to int. And modified contents of function test_exit_game in test_start_screen.py (modification is very small, just changing True to 1)
   + When quit_game == 2 restart game
   + When quit_game == 1 exit game
   + When quit_game == 0 loop continues
8. Created src/gui/info_box.py to rewrite InfoBox class. This is because there is a Close button in InfoBox, and I couldn't find a better way to change its text.
9. Added language-related UI in `Option menu`.

# 多语言支持说明
## 简介
这个更新为游戏添加了实现多语言功能的接口。由于翻译工作暂未完成，一些内容暂缺，但是无伤大雅，接口都已经完成了。

## 如何添加一门新的语言
1. 创建语言目录：在 `data` 文件夹下创建 en 文件夹的副本，重命名为您需要的语言名称，下面假定为 `language_name`。
2. 拷贝字体文件：在 `fonts` 文件夹下以 ttf 格式加入您的语言所需要的字体文件
3. 导入字体文件：修改 `data/language_name/fonts_description.py` 中的内容，将其中的字体文件的名字换成您所需要的字体文件的名字。
4. 添加语言按钮：修改 `menu_creater_manager.py` 中 `create_choose_language_menu` 函数中 `element_grid` 列表的内容。添加一个以您的语言的全称为 `title` 以 `language_name` 为 `callback` 的按钮。例如：
   ```python
    element_grid = [
        [Button(title="English", callback=lambda: buttons_callback("en"))],
        [Button(title="中文简体", callback=lambda: buttons_callback("zh_cn"))],
        ...
        [Button(title="Language Full Name", callback=lambda: buttons_callback("language_name"))],
    ]
   ```
5. 需要翻译的内容有：
    * `text.py` 中的字符串、函数输出和字典。
    * `data/language_name/maps/level_number` 下各个 txt 文件中的内容。
    * `data/language_name/maps/level_number` 下各个 map_properties.tmx 文件中的部分内容，包括：
        + level_name 的值。
        + main_mission_description 的值。
        + limited_mission_description 的值（如果存在）。
    * `data/language_name/` 下的 xml 部分文件中的部分内容。
        + `characters.xml` 中 `<talk>` 标签内的内容。
        + `alternations.xml` 中 `<info>` 标签内的内容。 
        + `items.xml` 中 `<info>` 标签内的内容。
        + `skills.xml` 中 `<info>` 和 `<name>` 标签内的内容。  
    请注意，以上修改的格式必须为： `<language_name> 翻译内容 </language_name>`。例如：
        ```xml
        ...
        <interaction>
            <talk>
                <en> Hurry up ! Leave ... the necropolis. </en>
                <zh_cn> 快呀！从...进入墓地。</zh_cn>
            </talk>
            <talk>
                <en> The clock is ticking... original place. </en>
                <zh_cn> 时钟在滴答...回原来的地方。 </zh_cn>
            </talk>
        </interaction>
        ...
        ```

# 修改与解释
1. 创建了 `src/gui/language.py` 用于处理语言相关的事情。`language.py` 会按照 `saves/options.xml` 中的语言导入相应的 `text.py`。
2. 将所有文件中涉及输出的静态字符串挪到了 `text.py` 的变量中，变量名由字符串的英文内容的大写和下划线组成。如果变量名的最后一个字符为下划线，说明字符串末尾是冒号。
3. 将所有文件中涉及变量且涉及输出的内容挪到 `text.py` 中以函数的方式处理。
4. 将所有文件中涉及类名且涉及输出的内容用 `text.py` 中的字典对应。（英文暂时保留原有的处理方法）
5. 改变读取 `data` 文件夹下的 xml 文件 `<info>` 或 `<talk>` 标签的方法。加入`<language_name>`标签。（但仍保留了原有的处理方法，因为翻译工作并未做完）
6. 在 `main.py` 添加了重启游戏相关的代码。用于在调整语言之后重启游戏。由于没有找到更好的重启游戏的方法，我使用创建子进程的方式实现重启游戏的功能。
7. 将各个 `Scene` 中传输给 `quit_game` 变量的返回值类型改为 `int`。并修改了 `test_start_screen.py` 中 `test_exit_game` 函数的内容。（修改很小，仅仅是`True`改为`1`）
   + 当 `quit_game == 2` 时重启游戏
   + 当 `quit_game == 1` 时退出游戏
   + 当 `quit_game == 0` 时循环继续
8. 创建了 `src/gui/info_box.py` 以重写 `InfoBox` 类。这是因为 `InfoBox` 中有一个 `Close` 按钮，我没有找到更好的使它改变文字的方法。
9. 在 `Option menu` 中添加了切换语言相关的UI。
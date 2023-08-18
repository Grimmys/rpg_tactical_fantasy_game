# RPG战术幻想游戏

[![使用Python制作](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![许可证](https://img.shields.io/github/license/Grimmys/rpg_tactical_fantasy_game)](https://github.com/Grimmys/rpg_tactical_fantasy_game/blob/master/LICENSE)
[![最新版本](https://img.shields.io/github/v/release/Grimmys/rpg_tactical_fantasy_game)](https://github.com/Grimmys/rpg_tactical_fantasy_game/releases/latest)
![GitHub最新版本下载量](https://img.shields.io/github/downloads/Grimmys/rpg_tactical_fantasy_game/latest/total)

**欢迎协作开发。**

这款游戏是一款2D回合制战术幻想RPG。

## 如何帮助开发

您可以通过发送电子邮件至grimmys.programming@gmail.com或者在GitHub上提交issue来提出任何请求或报告任何错误。

或者，您可以加入新创建的社区discord：https://discord.gg/CwFdXNs9Wt。

无论是关于编码实践还是游戏机制，都欢迎您提出想法，这个项目远非完美！

以下是一些贡献建议：

* 查看[已打开的问题](https://github.com/Grimmys/rpg_tactical_fantasy_game/issues)，有些错误可以修复，也有一些增强功能等待实现。
* 在整个项目中都可以找到很多TODO，其中一些对初学者来说很容易修复，而另一些则更具挑战性。
* 如果能帮助平衡游戏将不胜感激...我并不擅长这类游戏，即使我非常喜欢它们。所有数值都可以在data文件夹中的XML文件中找到。
* 如果能为声音效果或新的音轨做出贡献将非常感谢。

__版本__：1.0.4

![主屏幕显示可能的移动和攻击](/screenshots/player_moves_and_attacks.png?raw=True)
![物品栏菜单](/screenshots/inventory_screen.png?raw=True)
![状态窗口](/screenshots/status_screen.png?raw=True)

## 如何开始游戏

如果您使用的是64位Windows，您可以前往[发布页面](https://github.com/grimmys/rpg_tactical_fantasy_game/releases)获取预构建的可执行文件。

如果您希望直接从源代码运行（或者想要开发游戏），请确保安装了[Python3.9](https://python.org)（或更高版本），并在存储库文件夹中运行`python -m pip install -r requirements`。

然后，您可以在linux操作系统中运行`python main.py`或"./main.py"（仅适用于Python 3）来启动游戏。

## 按键

* 左键单击：选择玩家，选择移动位置，选择要执行的操作等（主按钮）
* 左键单击（在任何空白区域）：打开或关闭主菜单
* 左键单击（在任何非玩家实体上，且该玩家已完成回合）：打开一个窗口，显示有关该实体的信息
* 右键单击：取消选择玩家或取消上一次操作（如果可能）（辅助按钮）
* 右键单击（在任何实体上）：显示该实体的可能移动路径
* Esc键 ：关闭处于顶层的菜单

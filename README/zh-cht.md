# RPG戰術幻想遊戲

[![使用Python製作](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![許可證](https://img.shields.io/github/license/Grimmys/rpg_tactical_fantasy_game)](https://github.com/Grimmys/rpg_tactical_fantasy_game/blob/master/LICENSE)
[![最新版本](https://img.shields.io/github/v/release/Grimmys/rpg_tactical_fantasy_game)](https://github.com/Grimmys/rpg_tactical_fantasy_game/releases/latest)
![GitHub最新版本下載量](https://img.shields.io/github/downloads/Grimmys/rpg_tactical_fantasy_game/latest/total)

**歡迎協作開發。**

這款遊戲是一款2D回合制戰術幻想RPG。

## 如何幫助開發

您可以通過發送電子郵件至grimmys.programming@gmail.com或者在GitHub上提交issue來提出任何請求或報告任何錯誤。

或者，您可以加入新創建的社區discord：https://discord.gg/CwFdXNs9Wt。

無論是關於編碼實踐還是遊戲機制，都歡迎您提出想法，這個項目遠非完美！

以下是一些貢獻建議：

* 查看[已打開的問題](https://github.com/Grimmys/rpg_tactical_fantasy_game/issues)，有些錯誤可以修復，也有一些增強功能等待實現。
* 在整個項目中都可以找到很多TODO，其中一些對初學者來說很容易修復，而另一些則更具挑戰性。
* 如果能幫助平衡遊戲將不勝感激...我並不擅長這類遊戲，即使我非常喜歡它們。所有數值都可以在data文件夾中的XML文件中找到。
* 如果能為聲音效果或新的音軌做出貢獻將非常感謝。

__版本__：1.0.4

![主屏幕顯示可能的移動和攻擊](/screenshots/player_moves_and_attacks.png?raw=True)
![物品欄菜單](/screenshots/inventory_screen.png?raw=True)
![狀態窗口](/screenshots/status_screen.png?raw=True)

## 如何開始遊戲

如果您使用的是64位Windows，您可以前往[發布頁面](https://github.com/grimmys/rpg_tactical_fantasy_game/releases)獲取預構建的可執行文件。

如果您希望直接從源代碼運行（或者想要開發遊戲），請確保安裝了[Python3.9](https://python.org)（或更高版本），並在存儲庫文件夾中運行`python -m pip install -r requirements`。

然後，您可以在linux操作系統中運行`python main.py`或"./main.py"（僅適用於Python 3）來啟動遊戲。

## 按鍵

* 左鍵單擊：選擇玩家，選擇移動位置，選擇要執行的操作等（主按鈕）
* 左鍵單擊（在任何空白區域）：打開或關閉主菜單
* 左鍵單擊（在任何非玩家實體上，且該玩家已完成回合）：打開一個窗口，顯示有關該實體的信息
* 右鍵單擊：取消選擇玩家或取消上一次操作（如果可能）（輔助按鈕）
* 右鍵單擊（在任何實體上）：顯示該實體的可能移動路徑
* Esc鍵 ：關閉處於頂層的菜單

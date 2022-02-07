# PAIA 賽車機器學習平台

PAIA 賽車機器學習平台是一個可以用人工智慧去玩賽車遊戲的平台。

![gameshot](https://i.imgur.com/TTw50oI.jpg)



## 目錄
1. [遊戲下載及設定](#1)
2. [概覽](#2)
	* 2.1. [遊戲控制](#2_1)
	* 2.2. [道具](#2_2)
3. [PAIA 平台使用方法](#3)
	* 3.1. [主要的部分](#3_1)
	* 3.2. [環境建置](#3_2)
		* 3.2.1. [環境需求](#3_2_1)
		* 3.2.2. [環境變數（Environment Variables）](#3_2_2)
	* 3.3. [執行方式](#3_3)
		* 3.3.1. [線上（Online）模式](#3_3_1)
		* 3.3.2. [離線（Offline）模式](#3_3_2)
		* 3.3.3. [比賽模式](#3_3_3)
		* 3.3.4. [附註](#3_3_4)
4. [資料格式 Spec](#4)
	* 4.1. [狀態資訊](#4_1)
	* 4.2. [動作資訊](#4_2)
5. [PAIA 工具](#5)
	* 5.1. [影像資料轉換](#5_1)
	* 5.2. [省略圖片的位元資訊](#5_2)
	* 5.3. [產生動作 Action 物件](#5_3)
6. [資料收集（Demo Recorder）](#6)
7. [常見問題 FAQ](#7)



##  1. <a name='1'></a>遊戲下載及設定
Release：[PAIA Kart v1.0.1](https://github.com/timcsy/GameAIKart/releases/tag/v1.0.1)

解壓縮後，需要在 PAIA 資料夾底下進行：
- 修改 `.env.template` 檔，調整設定，並儲存成 `.env` 在同樣的目錄下（PAIA 資料夾底下）
  - Linux 或是 Mac 的用戶要記得先顯示隱藏的檔案
- 新增 `ml` 資料夾（或自訂名稱），並在底下加入：
  - `ml_play.py`：訓練用的檔案
  - `inferencing.py`：比賽或是使用訓練結果的檔案
  - 其他相關檔案
  - 請將 `.env` 檔底下的 `PLAY_BASE_DIR` 設為 `ml` 資料夾路徑（或剛剛自訂的名稱）
  - 如果要進行訓練
    - 請將 `.env` 檔底下的 `PLAY_SCRIPT` 設為 `"${PLAY_BASE_DIR}/ml_play.py"`
  - 如果要進行比賽或是使用訓練結果
    - 請將 `.env` 檔底下的 `PLAY_SCRIPT` 設為 `"${PLAY_BASE_DIR}/inferencing.py"`
- 記得安裝 Python 環境，參考下面的 [環境建置](#3_2)
  - 在 PAIA 資料夾下執行 `pip install -r requirements.txt`
- 其他設定請參閱以下文件



##  2. <a name='2'></a>概覽

###  2.1. <a name='2_1'></a>遊戲控制
如果使用手動模式，可以用方向鍵控制遊戲：
- 向上方向鍵：加速
- 向下方向鍵：減速或倒退
- 向左或向右方向鍵：左轉或右轉
- 方向鍵可以同時使用

###  2.2. <a name='2_2'></a>道具

| 油料（Gas） | 輪胎（Wheel） | 氮氣（Nitro） | 烏龜（Turtle） | 香蕉（Banana） |
|---|---|---|---|---|
| ![gas](https://user-images.githubusercontent.com/24825631/134625410-1458320f-49a2-44ac-9607-798d2a12f5ba.JPG) | ![wheel](https://user-images.githubusercontent.com/24825631/134625437-8472b5d1-fd00-45f1-a380-8ff18740d88d.JPG) | ![nitro](https://user-images.githubusercontent.com/24825631/134625458-288cac5a-4d49-433c-b81f-6d96e25a8dd4.JPG) | ![turtle](https://user-images.githubusercontent.com/24825631/134625493-76c6a6d2-4c6c-4962-9774-becfd7b6b838.JPG) | ![banana](https://user-images.githubusercontent.com/24825631/134625511-217e310f-31d0-4a7f-9d4d-7624d1d87137.JPG) |

在 .env 的 PLAY_PICKUPS 可以設定要不要使用道具。

#### 補充類道具

補充類道具如果用完就跑不動了，如果快沒了速度會變慢，所以要適時的補充。

- 油料：補充油料
- 輪胎：補充油料

#### 效果類道具

效果類道具會維持一段時間，有不同效果。

- 氮氣：加速
- 烏龜：減速
- 香蕉：打滑（影響轉動的量）



##  3. <a name='3'></a>PAIA 平台使用方法

###  3.1. <a name='3_1'></a>主要的部分
將你所寫的 `MLPlay` 類別放在 `ml/ml_play.py`（訓練腳本）、 `ml/ml_play.py`（比賽或使用訓練結果的腳本），可以改檔名（但是記得更新 PLAY_SCRIPT 環境變數），如下：
```python
import logging # you can use functions in logging: debug, info, warning, error, critical, log
from config import int_ENV
import PAIA
from demo import Demo

class MLPlay:
    def __init__(self):
        self.demo = Demo.create_demo() # create a replay buffer
        self.step_number = 0 # Count the step, not necessarily
        self.episode_number = 1 # Count the episode, not necessarily

    def decision(self, state: PAIA.State) -> PAIA.Action:
        '''
        Implement yor main algorithm here.
        Given a state input and make a decision to output an action
        '''
        # Implement Your Algorithm
        # Note: You can use PAIA.image_to_array() to convert
        #       state.observation.images.front.data and 
        #       state.observation.images.back.data to numpy array (range from 0 to 1)
        #       For example: img_array = PAIA.image_to_array(state.observation.images.front.data)
        MAX_EPISODES = int_ENV('MAX_EPISODES', -1)

        self.step_number += 1
        logging.info(f'Epispde: {self.episode_number}, Step: {self.step_number}')

        img_suffix = f'{self.episode_number}_{self.step_number}'
        logging.debug(PAIA.state_info(state, img_suffix))

        if state.event == PAIA.Event.EVENT_NONE:
            # Continue the game
            # You can decide your own action (change the following action to yours)
            action = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0)
            # You can save the step to the replay buffer (self.demo)
            self.demo.create_step(state=state, action=action)
        elif state.event == PAIA.Event.EVENT_RESTART:
            # You can do something when the game restarts by someone
            # You can decide your own action (change the following action to yours)
            action = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0)
            # You can start a new episode and save the step to the replay buffer (self.demo)
            self.demo.create_episode()
            self.demo.create_step(state=state, action=action)
        elif state.event != PAIA.Event.EVENT_NONE:
            # You can do something when the game (episode) ends
            want_to_restart = True # Uncomment if you want to restart
            # want_to_restart = False # Uncomment if you want to finish
            if (MAX_EPISODES < 0 or self.episode_number < MAX_EPISODES) and want_to_restart:
                # Do something when restart
                action = PAIA.create_action_object(command=PAIA.Command.COMMAND_RESTART)
                self.episode_number += 1
                self.step_number = 0
                # You can save the step to the replay buffer (self.demo)
                self.demo.create_step(state=state, action=action)
            else:
                # Do something when finish
                action = PAIA.create_action_object(command=PAIA.Command.COMMAND_FINISH)
                # You can save the step to the replay buffer (self.demo)
                self.demo.create_step(state=state, action=action)
                # You can export your replay buffer
                self.demo.export('kart.paia')
        
        logging.debug(PAIA.action_info(action))

        return action

    def autosave(self):
        '''
        self.autosave() will be called when the game restarts,
        You can save some important information in case that accidents happen.
        '''
        pass
```

修改 `decision` function，由 State 產生 Action。

請在 .env 的 PLAY_SCRIPT 指定以上腳本所在路徑。

注意路徑的問題，如果要取得相對於以上腳本的資料夾位置，

可以使用 `os.path.dirname(os.path.abspath(__file__))`，

可以參考 [Get Path of the Current File in Python](https://www.delftstack.com/howto/python/python-get-path/)，用 `__file__` 來獲取目前 Python script 所在的位置，

如果是一般相對的路徑，會以終端機所在的位置為準，兩者可能不同（腳本要假設可以放在任意資料夾下）。


###  3.2. <a name='3_2'></a>環境建置

####  3.2.1. <a name='3_2_1'></a>環境需求
- Python 3
  - mlagents==0.26.0
  - pytorch（安裝方式參考 [官網](https://pytorch.org/) ）
  - numpy
  - Pillow
  - opencv-python
  - paramiko
  - ffmpeg-python
  - python-dotenv

如果沒有自己的虛擬環境，建議使用 Anaconda。

在 PAIA 資料夾下執行 `pip install -r requirements.txt` 來安裝這些套件。

如果要啟動錄影功能，系統要再額外加裝 [ffmpeg](https://ffmpeg.org/download.html)。

####  3.2.2. <a name='3_2_2'></a>環境變數（Environment Variables）
Windows 設定：
```
SET PAIA_ID=小組的識別號碼
SET PAIA_HOST=小組的SSH主機IP
SET PAIA_PORT=小組的SSH主機port
SET PAIA_USERNAME=小組的SSH帳號
SET PAIA_PASSWORD=小組的SSH密碼
```

其他作業系統（Linux、macOS）設定：
```
export PAIA_ID=小組的識別號碼
export PAIA_HOST=小組的SSH主機IP
export PAIA_PORT=小組的SSH主機port
export PAIA_USERNAME=小組的SSH帳號
export PAIA_PASSWORD=小組的SSH密碼
```

如果沒有特別設定，在關閉終端機之後環境變數的設定會失效。

如果覺得每次都要設定環境變數很麻煩，或者覺得太複雜，「建議」使用 `.env` 設定檔進行設置，
Python 執行之前都會先匯入`.env` 設定檔中的環境變數。

請修改 `.env.template` 中的內容，並且存成 `.env`，可以參考 [dotenv](https://github.com/theskumar/python-dotenv) 的格式來做設定。

另外加上了一個 REQUIRE 變數，可以匯入其它 .env 檔。

在 Python 中獲取環境變數的方法：
```python
from config import ENV, bool_ENV, int_ENV, float_ENV
ENV['環境變數名稱'] # 取得環境變數
ENV['環境變數名稱'] = "值" # 設定環境變數（值一定要先轉換為字串！）
bool_ENV('環境變數名稱', 預設值) # 轉換環境變數為布林值，預設值可加可不加，不加的話是 None
int_ENV('環境變數名稱', 預設值) # 轉換環境變數為整數，預設值可加可不加，不加的話是 None
float_ENV('環境變數名稱', 預設值) # 轉換環境變數為浮點數，預設值可加可不加，不加的話是 None
```
ENV 用法和一般的 Python dict ㄧ樣，而且 ENV 的值「必須」為「字串」型態！

因此，提供了 `bool_ENV`, `int_ENV`, `float_ENV` 三個函數來方便作轉換。


有時候程式執行不起來是因為安全性設定，請先檢查一下下載下來的執行檔是否可以執行（詳見：[常見問題 FAQ](#FAQ)）。


###  3.3. <a name='3_3'></a>執行方式

藉由修改 `.env` 中的 RUNNING_MODE 環境變數，我們可以切換遊戲模式。

所以可以統一用以下簡單的指令執行：
```
python ml.py
```

如果要頻繁切換遊戲模式，可以考慮用下面的做法：

####  3.3.1. <a name='3_3_1'></a>線上（Online）模式
線上模式是指遊戲端和玩家端分別在不同的電腦跑。

遊戲端（與 Unity 在同一台機器上）：

設定 RUNNING_MODE=ONLINE，或是執行
```
python ml.py online
```

玩家端（用來做 training 或 inferencing 的）：

設定 RUNNING_MODE=PLAY，或是執行
```
python ml.py play
```

開啟順序：
開啟伺服器端 -> 執行玩家端（可以開始連進來）

####  3.3.2. <a name='3_3_2'></a>離線（Offline）模式
線上模式是指遊戲端和玩家端在同一台電腦跑。

自動（training 或 inferencing），為預設模式：

設定 RUNNING_MODE=OFFLINE，或是執行
```
python ml.py offline
```

手動（可以用來收集資料）：

設定 RUNNING_MODE=MANUAL，或是執行
```
python ml.py manual
```

####  3.3.3. <a name='3_3_3'></a>比賽模式
修改 `game/players.json`，會進行錄影。

跑比賽：

設定 RUNNING_MODE=GAME，或是執行
```
python ml.py game
```

####  3.3.4. <a name='3_3_4'></a>附註

環境變數 MAX_EPISODES 是最多跑幾回合遊戲就要結束，可以 `from config import int_ENV`，再用 `int_ENV('MAX_EPISODES', -1)` 取得。

因為有時候訓練會出現意想不到的錯誤，或是要中途開啟道具，所以平台設有中斷點，PLAY_CONTINUE 是說要不要從前一次中斷點繼續執行，PLAY_AUTOSAVE 是說要不要自動儲存中斷點。

如果想要錄製遊戲畫面，可以把 RECORDING_ENABLE 設為 true。

如果使用 Unity Editor，在 Restart 指令之後要自己重開遊戲，Build 版的就不用，會自動開啟。



##  4. <a name='4'></a>資料格式 Spec
參考 `communication/protos/PAIA.proto` 檔案

###  4.1. <a name='4_1'></a>狀態資訊
事件（`PAIA.Event`）定義，用法可以參考上面主要的部分的範例：
```C++
enum Event { // 事件
	EVENT_NONE; // 一般狀態
	EVENT_FINISH; // 結束（其他狀況）
	EVENT_RESTART; // 重新開始回合
	EVENT_WIN; // 結束（有在時限內完成）
	EVENT_TIMEOUT; // 超時
	EVENT_UNDRIVABLE; // 不能動了（用完油料或輪胎）
}
```

狀態資訊（`PAIA.State`）定義：
```C++
struct State { // 狀態資訊
	struct Observation { // 觀測資訊
		struct Ray { // 單一雷達資訊
			bool hit; // 是否在觀測範圍內
			float distance; // 距離（把最大觀測範圍當作 1）
		}
		struct RayList { // 所有雷達資訊
			Ray F; // 前方
			Ray B; // 後方
			Ray R; // 右方
			Ray L; // 左方
			Ray FR; // 前方偏向右方 30 度
			Ray RF; // 前方偏向右方 60 度
			Ray FL; // 前方偏向左方 30 度
			Ray LF; // 前方偏向左方 60 度
			Ray BR; // 後方偏向右方 45 度
			Ray BL; // 後方偏向左方 45 度
		}
		struct Image { // 影像資料
			bytes data; // 位元資訊
			int height; // 高（預設為 112）
			int width; // 寬（預設為 252）
			int channels; // 頻道數（預設為 RGB = 3）
		}
		struct ImageList { // 影像資料們
			Image front; // 前方的影像
			Image back; // 後方的影像
		}
		struct Refill { // 補充類道具
			float value; // 剩餘量
		}
		struct RefillList { // 補充類道具們（其中之一用完就動不了）
			Refill wheel; // 輪胎
			Refill gas; // 油料
		}
		struct Effect { // 效果類道具
			int number; // 作用中的道具數量
		}
		struct EffectList { // 效果類道具們
			Effect nitro; // 氮氣（加速）
			Effect turtle; // 烏龜（減速）
			Effect banana; // 香蕉（打滑）
		}
		RayList rays; // 雷達資料們
		ImageList images; // 影像資料們
		float progress; // 進度（把全部完成當作 1）
		float usedtime; // 經過的時間（秒）
		float velocity; // 速度
		RefillList refills; // 補充類道具們
		EffectList effects; // 效果類道具們
	}
	string api_version; // API 版本
	string id; // 使用者名稱
	Observation observation; // 觀察資料
	Event event; // 事件
	float reward; // 獎勵（由 Unity 端提供的）
}
```

###  4.2. <a name='4_2'></a>動作資訊
動作指令（`PAIA.Command`）定義，用法可以參考上面主要的部分的範例：
```C++
enum Command { // 想要做的指令
	COMMAND_GENERAL; // 一般動作
	COMMAND_START; // 開始
	COMMAND_FINISH; // 結束
	COMMAND_RESTART; // 重新開始
}
```

動作資訊（`PAIA.Action`）定義：
```C++
struct Action { // 動作資訊
	string api_version; // API 版本
	string id; // 使用者名稱
	Command command; // 動作指令
	bool acceleration; // 是否加速
	bool brake; // 是否減速
	float steering; // 轉彎（-1.0 ~ 1.0，0 是不轉，偏向 -1 式左轉，偏向 1 是右轉）
}
```



##  5. <a name='5'></a>PAIA 工具
PAIA 套件裡面有附一些工具，像是狀態（State）和動作（Action）的處理，可以使用。

下面會列舉一些會用到的，其他部分可以自行參考 `PAIA.py` 檔。

###  5.1. <a name='5_1'></a>影像資料轉換
`PAIA.State` 所提供的影像格式為 bytes 形式的 PNG，存放於影像類別觀察資料的 `data` 欄位中。
使用 `PAIA.image_to_array(data)` 可以轉換影像資料為 Numpy array 的形式：

例如：
```python
import PAIA

img_front = PAIA.image_to_array(state.observation.images.front.data)
img_back = PAIA.image_to_array(state.observation.images.back.data)
```
注意轉換後的影像為三維度的 Numpy array，值的範圍在 0 到 1 之間。


###  5.2. <a name='5_2'></a>省略圖片的位元資訊
因為在印出 State 或是 Action 時也會把當中的 image 所有位元都印出來，造成很大的不方便，

這裡提供了 `state_info()` 還有 `action_info()` 這兩個 function，會省略圖片，

或是如果 .env 裡面 IMAGE_ENABLE 環境變數有設為 true 的話，會將圖片存到指定資料夾。

用法：
```python
import PAIA

s = PAIA.State()
# 後綴檔名可以是圖片的編號（例如當前的回合、第幾步），也可以不加
text = str(PAIA.state_info(s, 後綴檔名)) # 把 s 的去影像化資訊轉成字串
print(text) # 顯示 s

a = PAIA.Action()
print(PAIA.action_info(a)) # 顯示 a
```

###  5.3. <a name='5_3'></a>產生動作 Action 物件
用法：
```python
import PAIA

a0 = PAIA.create_action_object(acceleration=False, brake=False, steering=0) # 不動
a1 = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0) # 往前走，不轉彎
a2 = PAIA.create_action_object(acceleration=True, brake=False, steering=-1.0) # 往前走，左轉
a3 = PAIA.create_action_object(acceleration=True, brake=False, steering=1.0) # 往前走，右轉
a4 = PAIA.create_action_object(acceleration=False, brake=True, steering=0.0) # 往後走或減速，不轉彎
a5 = PAIA.create_action_object(acceleration=False, brake=True, steering=-1.0) # 往後走或減速，左轉
a6 = PAIA.create_action_object(acceleration=False, brake=True, steering=1.0) # 往後走或減速，右轉
```



##  6. <a name='6'></a>資料收集（Demo Recorder）
Demo 除了記錄手動玩的結果，用來進行 Imitation Learning（模仿學習，像是 Behavior Cloning）以外，也可以用來儲存遊戲資訊。

DEMO_ENABLE 是空至曜不要錄製 Demo 的環境變數。

首先看到「步（Step）」的定義，類型為 `PAIA.Step`：
```C++
struct Step { // 一步的資訊
	State state; // 狀態資訊
	Action action; // 動作資訊
}
```

我們不論是在手動或自動跑遊戲時，都可以用 demo 套件來儲存 Step（State 和 Action）的資訊。
使用 `demo.Demo` 中的初始化可以讀入 `.paia` 檔。
使用 `demo.Demo` 中的 `export()` function 可以匯出成 `.paia` 檔，方便日後更快速讀入資料。

使用 `Demo` 類別讀取 / 匯出錄製的資料：
```python
from demo import Demo

# 在初始化時匯入資料
demo = Demo('.paia 檔的路徑')

# 在初始化時匯入資料（List 版本）
demo = Demo(['.paia 檔的路徑1', '.paia 檔的路徑2', ...])

# 匯入資料到最後
demo.load('.paia 檔的路徑')

# 匯入資料到最後（List 版本）
demo.load(['.paia 檔的路徑1', '.paia 檔的路徑2', ...])

# 匯出成 .paia 檔
demo.export('.paia 檔的路徑')

# 下面會產生一個新的空 Demo 物件
demo = Demo.create_demo()

# 下面會產生一個新的回合
demo.create_episode()

# 下面會產生一個新的 Step（包含 State 和 Action 的資訊）
demo.create_step(state=state, action=action)

# 使用 show() 函數可以顯示 demo 中的資訊
demo.show()

# 可以像 list 一樣存取資料（list 有的功能都可以），
# 例如下面取出 index 為 0 的回合，為一個 list
episode = demo[0]
# 例如下面取出 index 為 0 的回合的第 3 步，為一個 PAIA.Step 物件
step = demo[0][3]
print(step) # 印出 step 資訊，不省略圖片

# 除了用中括號 []，也可以用小括號 ()，依據環境變數 IMAGE_ENABLE 決定是否要儲存照片，
# 並且修改成方便轉換成字串顯示的形式（但圖片資料會被省略），
# 第一個參數為回合的 index，第二個參數為 Step 的 index
# 如果 index 是整數就是一般的 index，是 list 則是很多 index，是 None 代表全部
# 例如下面取出 index 為 0 的回合的所有 Step
step = demo(0)
# 例如下面取出 index 為 0 的回合的第 3 步
step = demo(0, 3)
print(step) # 印出 step 資訊，且省略圖片
# 例如下面取出 index 為 0, 1 的回合的各自的第 3、7 步
steps = demo([0, 1], [3, 7])
```



##  7. <a name='7'></a>常見問題 FAQ

Q：能不能使用相對路徑？

A：建議不使用，因為會發生執行環境當前路徑和腳本路徑不同的問題，所以建議使用 `os.path.dirname(os.path.abspath(__file__))` 來取得相對於腳本的資料夾。


Q：遊戲程式沒有跳出來怎麼辦？或是程式明明路徑是對的卻跳出 Provided filename does not match any environments？

A：可以看看是否為安全性問題，先是能不能手動開啟 App（終端機會顯示遊戲程式所在位置），每個系統有不同的解決方法，Windows 請參考：[將排除項目新增到 Windows 安全性](https://support.microsoft.com/zh-tw/windows/%E5%B0%87%E6%8E%92%E9%99%A4%E9%A0%85%E7%9B%AE%E6%96%B0%E5%A2%9E%E5%88%B0-windows-%E5%AE%89%E5%85%A8%E6%80%A7-811816c0-4dfd-af4a-47e4-c301afe13b26)，Mac 請參考：[在 Mac 上安全地開啟 App](https://support.apple.com/zh-tw/HT202491)。


Q：出現如下錯誤訊息？
```
TypeError: Invalid first argument to `register()`. typing.Dict[mlagents.trainers.settings.RewardSignalType, mlagents.trainers.settings.RewardSignalSettings] is not a class.
```

A：Python 3.9.10 以上目前與 mlagents-learn 套件不相容，請降級至3.9.9。參考：[Python 3.9.10 causes mlagents-learn not to work](https://github.com/Unity-Technologies/ml-agents/issues/5689)


Q：有一些 Module 不能使用，或是遇到 ModuleNotFoundError？

A：請先照前面的 [環境需求](#3_2_1) 安裝套件，記得要先切換到 PAIA 目錄底下（裡面才有 `requirements.py` 檔）。


Q：遇到 `pytorch` 的問題時？

A：看看是不是下錯指令，`pip` 要裝 `torch`，`conda` 才是裝 `pytorch`，請參考 [官網](https://pytorch.org/) 說明。


Q：如果遇到如以下的錯誤訊息該怎麼處理？
```
ERROR: Could not find a version that satisfies the requirement torch<1.9.0,>=1.8.0; platform_system != "Windows" and python_version >= "3.9" (from mlagents==0.26.0->-r requirements.txt (line 1)) (from versions: none)
ERROR: No matching distribution found for torch<1.9.0,>=1.8.0; platform_system != "Windows" and python_version >= "3.9" (from mlagents==0.26.0->-r requirements.txt (line 1))
```

A：建議可以升級 mlagents 到較新版本，例如 `pip install mlagents==0.27.0` 或是 `pip install mlagents==0.28.0`，如果還是不行的話可以考慮降級 pytorch 版本到他所建議的版本（像上面的錯誤訊息是說大於等於 1.8.0，小於 1.9.0 的版本），可以參考 [INSTALLING PREVIOUS VERSIONS OF PYTORCH](https://pytorch.org/get-started/previous-versions/)。


Q：出現如下錯誤訊息？
```
ImportError: cannot import name 'resolve_types' from 'attr' (/opt/anaconda3/lib/python3.8/site-packages/attr/__init__.py)
```

A：試試安裝 `pip install cattrs==1.0.0`。


Q：`python ml.py` 不能執行？

A：請先檢查是否已經經切換工作目錄到 PAIA 資料夾底下再執行。如果是使用虛擬環境（venv）或是 Anaconda 等，請確定是否切換到正確環境。


Q：我用 Command line 執行程式，但是遊戲好像有開起來不過一直黑畫面？

A：請檢查你的 PLAY_SCRIPT 環境變數對應到的路徑存不存在，像預設值會是 `ml/ml_play.py`（如果有自己指定的路徑可以自行修改成你要跑的腳本路徑）。


Q：出現像是下面的錯誤訊息？
```
self.actions[self.behavior_names[action.id]] = action
KeyError: 'xxx87'
```

A：把 .env 裡面的 PLAYER_ID 改成數字試試看。
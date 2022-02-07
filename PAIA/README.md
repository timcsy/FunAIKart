# PAIA 賽車機器學習平台

## 遊戲下載
Release：[PAIA Kart 1.0.0](https://github.com/timcsy/GameAIKart/releases/tag/1.0.0)

## 概覽
PAIA 賽車機器學習平台是一個可以用人工智慧去玩賽車遊戲的平台。

## 畫面

### 遊戲截圖
![gameshot](https://i.imgur.com/TTw50oI.jpg)

### 道具截圖

| 油料（Gas） | 輪胎（Wheel） | 氮氣（Nitro） | 烏龜（Turtle） | 香蕉（Banana） |
|---|---|---|---|---|
| ![gas](https://user-images.githubusercontent.com/24825631/134625410-1458320f-49a2-44ac-9607-798d2a12f5ba.JPG) | ![wheel](https://user-images.githubusercontent.com/24825631/134625437-8472b5d1-fd00-45f1-a380-8ff18740d88d.JPG) | ![nitro](https://user-images.githubusercontent.com/24825631/134625458-288cac5a-4d49-433c-b81f-6d96e25a8dd4.JPG) | ![turtle](https://user-images.githubusercontent.com/24825631/134625493-76c6a6d2-4c6c-4962-9774-becfd7b6b838.JPG) | ![banana](https://user-images.githubusercontent.com/24825631/134625511-217e310f-31d0-4a7f-9d4d-7624d1d87137.JPG) |

## 遊戲控制（手動）
* 向上方向鍵：加速
* 向下方向鍵：減速或倒退
* 向左或向右方向鍵：左轉或右轉
* 方向鍵可以同時使用

## 遊戲道具

在 .env 的 PLAY_PICKUPS 可以設定要不要使用道具。

### 補充類道具

補充類道具如果用完就跑不動了，如果快沒了速度會變慢，所以要適時的補充。

* 油料：補充油料
* 輪胎：補充油料

### 效果類道具

效果累到聚會維持一段時間，有不同效果。

* 氮氣：加速
* 烏龜：減塑
* 香蕉：打滑（影響轉動的量）


## 使用方法

### 主要的部分
將你所寫的 `MLPlay` 類別放在 `ml/ml_play.py` （可以改檔名）中，如下：
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

注意路徑的問題，如果要取得相對於 `ml_play.py` 的資料夾位置，

可以使用 `os.path.dirname(os.path.abspath(__file__))`，

可以參考 [Get Path of the Current File in Python](https://www.delftstack.com/howto/python/python-get-path/)，用 `__file__` 來獲取目前 Python script 所在的位置，

如果是一般相對的路徑，會以終端機所在的位置為準，兩者可能不同（`ml_play.py` 要假設可以放在任意資料夾下）。

### 環境建置

#### 環境需求
* Python 3
* mlagents==0.26.0
* pytorch
* numpy
* Pillow
* opencv-python
* paramiko
* ffmpeg-python
* python-dotenv

建議使用 Anaconda，

執行 `pip install -r requirements.txt` 來安裝這些套件。

#### 環境變數（Environment Variables）
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
export \
PAIA_ID=小組的識別號碼 \
PAIA_HOST=小組的SSH主機IP \
PAIA_PORT=小組的SSH主機port \
PAIA_USERNAME=小組的SSH帳號 \
PAIA_PASSWORD=小組的SSH密碼
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


有時候程式執行不起來是因為安全性設定，請先檢查一下下載下來的執行檔是否可以執行。

### 執行方式

藉由修改 `.env` 中的 RUNNING_MODE 環境變數，我們可以切換遊戲模式。

所以可以統一用以下簡單的指令執行：
```
python ml.py
```

如果要頻繁切換遊戲模式，可以考慮用下面的做法：

#### 線上（Online）模式
遊戲端（與 Unity 在同一台機器上）：
```
python ml.py online
```

玩家端（用來作 training 或 inferencing 的）：
```
python ml.py play
```

開啟順序：
開啟伺服器端 -> 執行玩家端（可以開始連進來）

#### 離線（Offline）模式
自動（training 或 inferencing）：
```
python ml.py offline
```

手動（可以用來收集資料）：
```
python ml.py manual
```

#### 比賽模式
修改 `game/players.json`，會進行錄影
```
python ml.py game
```

#### 附註
如果使用 Unity Editor，在 Restart 指令之後要自己重開遊戲，Build 版的就不用，會自動開啟。


## 資料格式 Spec
參考 `communication/protos/PAIA.proto` 檔案

### 狀態資訊
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
			int height; // 高
			int width; // 寬
			int channels; // 頻道數（RGB = 3）
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

### 動作資訊
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

## PAIA 工具
PAIA 套件裡面有一些工具，像是狀態（State）和動作（Action）的處理，可以使用。

下面會列舉一些，其他部分可以自行參考 `PAIA.py` 檔。

### 影像資料轉換
`PAIA.State` 所提供的影像格式為 bytes 形式的 PNG，存放於影像類別觀察資料的 `data` 欄位中。
使用 `PAIA.image_to_array(data)` 可以轉換影像資料為 Numpy array 的形式：

例如：
```python
import PAIA

img_front = PAIA.image_to_array(state.observation.images.front.data)
img_back = PAIA.image_to_array(state.observation.images.back.data)
```
注意轉換後的影像為三維度的 Numpy array，值的範圍在 0 到 1 之間。


## 資料收集（Demo Recorder）
Demo 除了記錄手動玩的結果，用來進行 Imitation Learning（模仿學習，像是 Behavior Cloning）以外，也可以用來當作 Replay Buffer 使用。

首先看到「步（Step）」的定義，為一個 `PAIA.Step`：
```C++
struct Step { // 一步的資訊
	State state; // 狀態資訊
	Action action; // 動作資訊
}
```

我們不論是在手動或自動跑遊戲時，都可以用 demo 套件來儲存 Step（State 和 Action）的資訊。
使用 `demo.Demo` 中的初始化可以讀入 `.paia` 檔。
使用 `demo.Demo` 中的 `export()` function 可以匯出成 `.paia` 檔，方便日後更快速讀入資料。

使用 `Demo` 類別讀取/匯出錄製的資料：
```python
from demo import Demo

# 在初始化時匯入資料
demo = Demo('.paia 檔的路徑')

# 在初始化時匯入資料（List 版本）
demo = Demo(['.paia 檔的路徑1', '.paia 檔的路徑2', ...])

# 匯入資料到後面
demo.load('.paia 檔的路徑')

# 匯入資料到後面（List 版本）
demo.load(['.paia 檔的路徑1', '.paia 檔的路徑2', ...])

# 匯出成 .paia 檔
demo.export('.paia 檔的路徑')

# 下面會產生一個新的空 Demo 物件
demo = Demo.create_demo()

# 下面會產生一個新的回合
demo.create_demo()

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
# 例如下面取出 index 為 0 的回合的第 3 步
step = demo(0, 3)
print(step) # 印出 step 資訊，且省略圖片
# 例如下面取出 index 為 0, 1 的回合的各自的第 3、7 步
steps = demo([0, 1], [3, 7])
```

## FAQ
Q1：遊戲程式沒有跳出來怎麼辦？
A1：可以看看是否為安全性問題，每個系統有不同的解決方法。

Q2：能不能使用相對路徑？
A2：建議不使用，因為會發生執行環境當前路徑和腳本路徑不同的問題，所以建議使用 `os.path.dirname(os.path.abspath(__file__))` 來取得相對於腳本的資料夾。
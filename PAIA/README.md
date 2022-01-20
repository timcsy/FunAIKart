# PAIA 賽車機器學習平台

## 使用方法

### 主要的部分
將你所寫的 `MLPlay` 類別放在 `ml_play.py` （可以改檔名）中，如下：
```python
import logging # you can use functions in logging: debug, info, warning, error, critical, log
import config
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
        
        self.step_number += 1
        logging.info('Epispde: ' + str(self.episode_number) + ', Step: ' + str(self.step_number))

        img_suffix = str(self.episode_number) + '_' + str(self.step_number)
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
            if self.episode_number < config.MAX_EPISODES and want_to_restart:
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
```
修改 `decision` function，由 State 產生 Action。

### 執行方式（修改中）

#### 目前測試版本
伺服器端（與 Unity 在同一台機器上）：
```
python server.py 執行檔位置(如果沒有加這項就是使用 Unity Editor)
```
用戶端（用來作 training 或 inferencing 的）：
```
python client.py 使用者id ml_play_檔名.py
```
離線（Offline）模式，目前只支援 Unity Editor：
```
python ml.py offline 使用者id ml_play_檔名.py
```
Demo 錄製檔案的位置（Unity Editor）：
```
根目錄/PAIA/Demo
```
Demo 錄製檔案的位置（Build 好的執行檔）：
```
執行檔所在目錄/PAIA/Demo
```

附註：如果使用 Unity Editor，在 Restart 指令之後要自己重開遊戲，Build 版的就不用，會自動開啟。

#### 線上（Online）模式（未完成）
伺服器端（與 Unity 在同一台機器上）：
```
python ml.py server -p 50051
```

用戶端（用來作 training 或 inferencing 的）：
```
python ml.py client 使用者id ml_play_檔名.py 使用者id2 ml_play_檔名2.py ...
```

開啟順序：
開啟伺服器端 -> 執行 Unity 遊戲、用戶端（可以開始連進來）

#### 離線（Offline）模式（未完成）
```
python ml.py offline 使用者id1 ml_play_檔名1.py 使用者id2 ml_play_檔名2.py ...
```

開啟順序：
執行離線版 -> 執行 Unity 遊戲

#### 參數說明（未完成）
- -h, --help
- -v, --verbose
- -V, --version
- -m, --manual
  - restart times
- offline
  - -r, --record
  	- demo path
  - -e, --env
  - -p, --port
  - players
  	- id code ...
- server
  - -r, --record
  	- demo path
  - -e, --env
  - -p, --port
  - -n, --player-number
- client
  - -a, --server-address
  - -r, --record
  	- demo path
  - players
  	- id code ...

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

### Demo 檔案處理
在手動玩 Unity 時，可以使用 Demonstration Recorder 收集資料。

在 Unity 當中可以設定 Agent 的 Demonstration Recorder
是否運作以及放置 `.demo` 檔的路徑（預設值為：根目錄/PAIA/Demo）。

使用 `demo.Demo` 中的初始化可以讀入 `.demo` 或是 `.paia` 檔。
使用 `demo.Demo` 中的 `export()` function 可以將 `.demo` 匯出成 `.paia` 檔，方便日後更快速讀入資料。

注意：`PAIA.Demo` 和 `demo.Demo` 不一樣，前者是 Protocol Buffers 的定義，後者是用來讀取錄製資料的類別。

使用 `Demo` 類別讀取/匯出錄製的資料：
```python
from demo import Demo

# 匯入資料
demo = Demo('.demo 或 .paia 檔的路徑')

# 匯入資料（List 版本）
demo = Demo(['.demo 或 .paia 檔的路徑1', '.demo 或 .paia 檔的路徑2', ...])

# 匯出成 .paia 檔
demo.export('.paia 檔的路徑')

# 存取全部資料
data = demo.demo
# 或是
data = demo.get_demo()

# 單個 Episode
episode = demo.get_episode(episode)

# 所有 Episode
episodes = demo.get_episodes()

# 單個 Step
step = demo.get_step(episode, step)

# Episode 中的所有 Step
steps = demo.get_steps(episode)

# 單個 State
state = demo.get_state(episode, step)

# Episode 中的所有 State
states = demo.get_states(episode)

# 單個 Action
action = demo.get_action(episode, step)

# Episode 中的所有 Action
actions = demo.get_actions(episode)
```

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

### 錄製資訊
錄製資訊除了記錄手動玩的結果，用來進行 Imitation Learning（模仿學習）以外，也可以用來當作 Replay Buffer 使用，以下的格式均是使用 [Protocol Buffer](https://developers.google.com/protocol-buffers)，可以參考官方說明裡面的使用方法來使用，如果是陣列（Array）/列表（List）的畫也可以善用 Python 的 `append(元素)` 新增單筆資料或是`extend(列表)` 新增多筆資料。

「步（Step）」的資訊（`PAIA.Step`）定義：
```C++
struct Step { // 一步的資訊
	State state; // 狀態資訊
	Action action; // 動作資訊
}
```

回合資訊（`PAIA.Episode`）定義：
```C++
struct Episode { // 回合資訊
	Step[] steps; // 所有步的資訊（是一個陣列/List）
}
```
一回合裡面有多個「步」。

錄製資訊（`PAIA.Demo`）定義：
```C++
struct Demo { // 錄製資訊
	Episode[] episodes; // 所有回合的資訊（是一個陣列/List）
}
```
一個錄製資訊裡面有多個回合。
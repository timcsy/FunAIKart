# PAIA 賽車機器學習平台

## 使用方法

### 主要的部分
將你所寫的 `MLPlay` 類別放在 `ml_play.py` 中，如下：
```python
import PAIA
from utils import debug_print

class MLPlay:
    def __init__(self):
        self.step = 0 # Count the step, not necessarily

    def decision(self, state: PAIA.State) -> PAIA.Action:
        '''
        Implement yor main algorithm here.
        Given a state input and make a decision to output an action
        '''
        # Implement Your Algorithm
        # Note: You can use PAIA.image_to_array() to convert
        #       state.observation.images.front.data and 
        #       state.observation.images.back.data to numpy array
        #       For example: img_array = PAIA.image_to_array(state.observation.images.front.data)
        self.step += 1
        debug_print('Step:', self.step)
        debug_print(PAIA.state_info(state, self.step))
        action = PAIA.create_action_object(acceleration=True, brake=False, steering=0.0)
        return action
```
修改 `decision` function，由 State 產生 Action。

### 執行方式
伺服器端（與 Unity 在同一台機器上）：
```
python ml.py server
```

用戶端（用來作 training 或 inferencing 的）：
```
python ml.py client -n 使用者id
```

開啟順序：
伺服器端 -> 執行 Unity 遊戲本身 -> 用戶端（可以開始連進來）


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
事件（`PAIA.Event`）定義：
```C++
enum Event { // 事件
	EVENT_NONE; // 一般狀態
	EVENT_FINISH; // 結束
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
Action 狀態（`PAIA.Status`）定義：
```C++
enum Status { // 想要做的指令
	STATUS_NONE; // 一般狀態
	STATUS_START; // 開始
	STATUS_FINISH; // 結束
	STATUS_RESTART; // 重新開始
}
```

動作資訊（`PAIA.Action`）定義：
```C++
struct Action { // 動作資訊
	string api_version; // API 版本
	string id; // 使用者名稱
	Status status; // 想要做的指令
	bool acceleration; // 是否加速
	bool brake; // 是否減速
	float steering; // 轉彎（-1.0 ~ 1.0，0 是不轉，偏向 -1 式左轉，偏向 1 是右轉）
}
```

### 錄製資訊
步的資訊（`PAIA.Step`）定義：
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

錄製資訊（`PAIA.Demo`）定義：
```C++
struct Demo { // 錄製資訊
	Episode[] episodes; // 所有回合的資訊（是一個陣列/List）
}
```
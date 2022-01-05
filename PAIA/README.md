# PAIA 賽車機器學習平台

## 使用方法

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
伺服器端 -> Unity 遊戲本身 -> 用戶端（可以開始連進來）


### 影像資料轉換
`PAIA.State` 所提供的影像格式為 bytes 形式的 PNG，存放於影像類別觀察資料的 `data` 欄位中。
使用 `PAIA.image_to_array(data)` 可以轉換影像資料為 Numpy array 的形式：

例如：
```
import PAIA

img_front = PAIA.image_to_array(state.observation.images.front.data)
img_back = PAIA.image_to_array(state.observation.images.back.data)
```
注意轉換後的影像為三維度的 Numpy array，值的範圍在 0 到 1 之間。

### Demo 檔案處理
注意：`PAIA.Demo` 和 `demo.Demo` 不一樣，前者是 Protocol Buffers 的定義，後者是用來讀取錄製資料的類別。

使用 `Demo` 類別讀取/匯出錄製的資料：
```
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

### 狀態資訊 `PAIA.State`
事件（`PAIA.Event`）定義：
```
enum Event {
	EVENT_NONE = 0;
	EVENT_FINISH = 1;
	EVENT_TIMEOUT = 2;
	EVENT_UNDRIVABLE = 3;
}
```

狀態資訊（`PAIA.Event`）定義：
```
message State {
  message Observation {
		message Ray {
			optional bool hit = 1;
			optional float distance = 2;
		}
		message RayList {
			optional Ray F = 1;
			optional Ray B = 2;
			optional Ray R = 3;
			optional Ray L = 4;
			optional Ray FR = 5;
			optional Ray RF = 6;
			optional Ray FL = 7;
			optional Ray LF = 8;
			optional Ray BR = 9;
			optional Ray BL = 10;
		}
		message Image {
			optional bytes data = 1;
			optional int32 height = 2;
			optional int32 width = 3;
			optional int32 channels = 4;
		}
		message ImageList {
			optional Image front = 1;
			optional Image back = 2;
		}
		message Refill {
			optional float value = 1;
		}
		message RefillList {
			optional Refill wheel = 1;
			optional Refill gas = 2;
		}
		message Effect {
			optional int32 number = 1;
		}
		message EffectList {
			optional Effect nitro = 1;
			optional Effect turtle = 2;
			optional Effect banana = 3;
		}
		optional RayList rays = 1;
		optional ImageList images = 2;
		optional float progress = 3;
		optional float velocity = 4;
		optional RefillList refills = 5;
		optional EffectList effects = 6;
	}
	optional string api_version = 1;
	optional string id = 2;
	optional Observation observation = 3;
	optional Event event = 4;
	optional float reward = 5;
}
```

### 動作資訊 `PAIA.Action`
Action 狀態（`PAIA.Status`）定義：
```
enum Status {
	STATUS_NONE = 0;
	STATUS_START = 1;
	STATUS_FINISH = 2;
	STATUS_RESTART = 3;
}
```

動作資訊（`PAIA.Action`）定義：
```
message Action {
	optional string api_version = 1;
	optional string id = 2;
	optional Status status = 3;
	optional bool acceleration = 4;
	optional bool brake = 5;
	optional float steering = 6;
}
```

### 錄製資訊 `PAIA.Demo`
步的資訊（`PAIA.Step`）定義：
```
message Step {
	optional State state = 1;
	optional Action action = 2;
}
```

回合資訊（`PAIA.Step`）定義：
```
message Episode {
	repeated Step steps = 1;
}
```

錄製資訊（`PAIA.Step`）定義：
```
message Demo {
	repeated Episode episodes = 1;
}
```
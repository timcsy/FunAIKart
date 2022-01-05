## 使用方法

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
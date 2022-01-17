# ML-Agents
This Branch has been heavily modified in order to support the training of ML-Agents. The correct NN-Model has already been applied. There are currently 3 trained Models in Assets/PAIA folder. Scenes can be found in Assets/Karting/Scenes folder.
- **Kart**: Continous. Trained in MainScene. Most unstable.
- **Kart_New**: Discrete. Trained in MainScene. Rather Stable.
- **Complex**: Discrete. Stacked Vector = 2. Trained in MainScene02. Rather Stable.

PAIAKart GameObject uses **Kart** model; PAIAKart_New can use both **Kart_New** and **Complex** *. Remember to change the **CinemachineVirtualCamera** as well if you wish to change the kart.

*With a few differences you need to change

## How to Install ML-Agents
1. Open the env folder in terminal. `>cd env`
2. Activate the virtual environment. `~\env>Scripts\activate`
3. Update pip. `(env) ~\env>python -m pip install --upgrade pip`
4. Install ML-Agent. `(env) ~\env>pip install mlagents`

## How to Train ML-Agents
1. Open the env folder in terminal. `~>cd env`
2. Activate the virtual environment. `~\env> Scripts\activate`
3. Run Ml-Agent: `(env) ~\env> mlagents-learn config/Complex.yaml --run-id=Complex --resume`
- Config files are in `env\config\`. Refer to above for the 3 versions.
- Trained models are in `env\results\`. You need to drag them into `Assets` for them to show up in Unity. (I put them in `Assets\PAIA\`.
- Few recorded Demo files are in `env\Demo\`, and are used by the config for imitational learning.
- Remember to remove the applied NN Model and set **Behavior Type** to **Default** on the Kart gameobjects before you start training.

## Additional Resources:
- ML-Agent Tutorial: https://youtu.be/zPFU30tbyKs
- Ml-Agent to Gym: https://github.com/Unity-Technologies/ml-agents/blob/main/gym-unity/README.md

# GameAIKart
This is a Full project folder, you can click Add on the Unity Hub to open the project after downloading.

## Table of contents
- [GameAIKart](#gameaikart)
  - [Table of contents](#table-of-contents)
  - [Overview](#overview)
  - [Examples](#examples)
  - [Game Controls](#game-controls)
  - [Game Props](#game-props)
    - [Supplementary props](#supplementary-props)
    - [Usage Props](#usage-props)
  - [Additional Track](#additional-track)
  - [Technologies](#technologies)
  - [Usage](#usage)
  - [ML-Agents](#ml-agents)

## Overview
GameAIKart is a 3D racing game made in Unity. We designed it to let everyone can build each type of scene for training the AIKart.

## Examples

> Screenshot of the game
![gameshot](https://user-images.githubusercontent.com/24825631/134624419-dc6c39ba-17d3-4cc8-bce6-ef6a466e54d4.jpg)

> Screenshot of the game props

| Gas | Wheel | Nitro | Turtle | Banana |
|---|---|---|---|---|
| ![gas](https://user-images.githubusercontent.com/24825631/134625410-1458320f-49a2-44ac-9607-798d2a12f5ba.JPG) | ![wheel](https://user-images.githubusercontent.com/24825631/134625437-8472b5d1-fd00-45f1-a380-8ff18740d88d.JPG) | ![nitro](https://user-images.githubusercontent.com/24825631/134625458-288cac5a-4d49-433c-b81f-6d96e25a8dd4.JPG) | ![turtle](https://user-images.githubusercontent.com/24825631/134625493-76c6a6d2-4c6c-4962-9774-becfd7b6b838.JPG) | ![banana](https://user-images.githubusercontent.com/24825631/134625511-217e310f-31d0-4a7f-9d4d-7624d1d87137.JPG) |

## Game Controls
* press "up" key to accelerate
* press "left" and "right" keys to turn
* press "down" key to go backwards

## Game Props
### Supplementary props 
* "Gas" : Replenish gas
* "Wheel" : Replenish wheel

### Usage Props
* "Nitro" : Increase speed
* "Turtle" : Decrease speed
* "Banana" : Influence the value of steer

## Technologies
* Unity 2020.3.14f1

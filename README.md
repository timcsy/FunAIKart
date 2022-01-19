# GameAIKart
This is a Full project folder, you can click Add on the Unity Hub to open the project after downloading, and the game scene is in Assets/Karting/Scenes/PAIAScene.

## Table of contents
- [GameAIKart](#gameaikart)
  - [Table of contents](#table-of-contents)
  - [Overview](#overview)
  - [Examples](#examples)
  - [Game Controls](#game-controls)
  - [Game Props](#game-props)
    - [Supplementary props](#supplementary-props)
    - [Usage Props](#usage-props)
  - [Technologies](#technologies)
  - [Usage](#usage)
  - [PAIA 機器學習平台](#paia-機器學習平台)

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

## Usage
This repository contains everything needed to get the project up and running on Unity. Just clone the repository and open the project in Unity to edit the game yourself.

遊戲場景在 Assets/Karting/Scenes/PAIAScene，只要 Build 這個場景就好！

## PAIA 機器學習平台
機器學習的部分放在 `PAIA` 資料夾中，使用方法請參考：[PAIA 賽車機器學習平台](PAIA)

注意：Python Unity 的 ML-Agents 的版本要對好，本專案用的是 Release 17
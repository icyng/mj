# 麻雀手牌解析ツール(仮)

麻雀での手配状況を解析し、逐次可視化

icyng、update：2024/10/28

---

## 概要

- 「物体検知を用いて麻雀の手配解析をする」
- 機能：
  - [x] 手元カメラ：手牌解析（acc 0.95）
  - [ ] 天井カメラ：捨牌・ドラ・鳴き解析
  - [ ] 天井での解析をもとに、手牌に対して「待ち」や「和了」の実装

## 仕様

- 実行環境：M1 mac air, win 11
- データ元：[abemaの配信キャプチャ](https://abema.tv/video/genre/mahjong)
- データ作成(annotation)：[Label-Studio](https://labelstud.io/)
- 物体検知：[YOLOv8](https://docs.ultralytics.com/)

## todo

- とりあえず天カメのアノテーション
  - 学習できるかわからないのでfew-shot
  - 一旦、鳴き・捨て牌・ドラのみ
- 終わったら、天カメデータと手元データを連動
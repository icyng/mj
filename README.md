# 麻雀手牌解析ツール(仮)

麻雀での手配状況を解析し、随時可視化するスクリプト

著：icyng、更新日：2024/07/16

---

## 概要

- 「物体検知を用いて麻雀の手配解析をする」
- 機能：
  - 手牌表示のみ（今のところ）
  - 表示というよりかは、生のデータを出力する解析機としての役割

## 環境

- 実行環境：**著者の場合**、M1 mac air（基本 win と同じ）
- データ元：[abemaの配信キャプチャ](https://abema.tv/video/genre/mahjong)
- データ作成(annotation)：[Label-Studio](https://labelstud.io/)
- 物体検知モデル：[YOLOv8](https://docs.ultralytics.com/)

## 注意事項

- 扱う画像について
  - サイズは`1620 x 908`で、形式は`jpg`
  - 似たような画像はできる限り排除する（2,3枚ほどが許容範囲内）
- データのエクスポートについて
  - 1つのフォルダが全てアノテーション済みになった場合にかぎり行なう
  - データ管理が少しややこしくなってしまう
  - 同じ環境を使用していれば、作業途中のデータも残る（はず）

## 事前準備

#### 1. 最低限の準備

始めにやること（Python3 以上が導入済みであること）
まず仮想環境を作成しアクティブにする

```bash
cd ~
python3 -m venv env
# mac
source env/bin/activate
# win
.venv\Scripts\activate.bat
```

作ったら label-studio をインストール

```bash
python -m pip install label-studio
```

実行の前に、コマンドで`export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true` を実行しておく事を推奨する（win : export を set に置換）

```bash
# 実行
label-studio start
```

初回はログインが必要、http://localhost:8080 を開いてログインまでできる事を確認したら、早速作業に入る

#### 2. プロジェクト設定

1. *Create Project* をクリックする
   1. *Project Name* はなんでもいい
   2. *Labeling Setup* を開き、*Computer Vision* の中の *Object Detection with Bounding Boxes* を押す
   3. 真ん中の上あたりに *[ Code / Visual ]* とある、初期設定では *Visual* になっているので *Code* をクリックし、ページ下部にある付録セクションのコードをコピーして書き換える
2. 出来上がったプロジェクトの *Settings* を開く
   1. *Settings* > *Cloud Storage* > *Add Source Storage* の順にクリック
   2. *Storage Type* を *Local files* に設定し、*Absolute local path* にデータの入っているフォルダの絶対パスを入力
   3. *Add Strage* -> *Sync Storage* で設定は終了

## アノテーション手順

- 具体的に書かずとも、UIがかなり綺麗なので大丈夫だと思う
- 一応、[このページ](https://note.com/asahi_ictrad/n/n9e80d4d516ad) がすごくわかりやすかったのでご参考に

## モデル作成手順

Coming soon ...

## 付録

コードファイルは `code.labelstudio.txt`

```code
<View>
    <Image name="image" value="$image" zoom="true" zoomControl="true" rotateControl="true"/>
    <View>
        <Filter toName="label" minlength="0" name="filter"/>
        <Header value="$value" />
        <RectangleLabels name="label" toName="image" strokeWidth="3" opacity="0.1">
            <Label value="1m" background="#00b52e"/>
            <Label value="2m" background="#bd601b"/>
            <Label value="3m" background="#7cb2ae"/>
            <Label value="4m" background="#a74586"/>
            <Label value="5m" background="#746e61"/>
            <Label value="5mr" background="#ff01aa"/>
            <Label value="6m" background="#db5017"/>
            <Label value="7m" background="#0490a9"/>
            <Label value="8m" background="#d98d96"/>
            <Label value="9m" background="#39e109"/>
            <Label value="1s" background="#b4b0f2"/>
            <Label value="2s" background="#70fe9f"/>
            <Label value="3s" background="#0c9030"/>
            <Label value="4s" background="#0f3473"/>
            <Label value="5s" background="#2ff21e"/>
            <Label value="5sr" background="#0022fa"/>
            <Label value="6s" background="#625aae"/>
            <Label value="7s" background="#67ab95"/>
            <Label value="8s" background="#eb50f0"/>
            <Label value="9s" background="#b1caea"/>
            <Label value="1p" background="#76da3c"/>
            <Label value="2p" background="#d67024"/>
            <Label value="3p" background="#644f43"/>
            <Label value="4p" background="#d4363e"/>
            <Label value="5p" background="#6cd6f7"/>
            <Label value="5pr" background="#00d6f7"/>
            <Label value="6p" background="#59fb8f"/>
            <Label value="7p" background="#6c1b3d"/>
            <Label value="8p" background="#7946fd"/>
            <Label value="9p" background="#c26255"/>
            <Label value="ton" background="#7ed4c2"/>
            <Label value="nan" background="#08681d"/>
            <Label value="sha" background="#0b01f9"/>
            <Label value="pei" background="#440bbc"/>
            <Label value="hak" background="#dd3589"/>
            <Label value="hat" background="#992aa4"/>
            <Label value="tyn" background="#f8f859"/>
        </RectangleLabels>
    </View>
</View>
```
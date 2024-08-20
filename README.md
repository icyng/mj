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
        <Header value="$value"/>
        <RectangleLabels name="label" toName="image" strokeWidth="3" opacity="0.1">
            <Label value="1m" background="#FF0000" hotkey="1"/>
            <Label value="2m" background="#FF1E1E" hotkey="2"/>
            <Label value="3m" background="#FF3C3C" hotkey="3"/>
            <Label value="4m" background="#FF5A5A" hotkey="4"/>
            <Label value="5m" background="#FF7878" hotkey="5"/>
            <Label value="6m" background="#FF9696" hotkey="6"/>
            <Label value="7m" background="#FFB4B4" hotkey="7"/>
            <Label value="8m" background="#FFD2D2" hotkey="8"/>
            <Label value="9m" background="#FFF0F0" hotkey="9"/>
            <Label value="5mr" background="#FF01FF" hotkey="0"/>
            <Label value="1s" background="#00FF00" hotkey="q"/>
            <Label value="2s" background="#00FF1E" hotkey="w"/>
            <Label value="3s" background="#00FF3C" hotkey="e"/>
            <Label value="4s" background="#00FF5A" hotkey="r"/>
            <Label value="5s" background="#00FF78" hotkey="t"/>
            <Label value="6s" background="#00FF96" hotkey="y"/>
            <Label value="7s" background="#00FFB4" hotkey="u"/>
            <Label value="8s" background="#32FFB4" hotkey="i"/>
            <Label value="9s" background="#64FFB4" hotkey="o"/>
            <Label value="5sr" background="#F218DF" hotkey="p"/>
            <Label value="1p" background="#0000FF" hotkey="a"/>
            <Label value="2p" background="#001EFF" hotkey="s"/>
            <Label value="3p" background="#003CFF" hotkey="d"/>
            <Label value="4p" background="#005AFF" hotkey="f"/>
            <Label value="5p" background="#0078FF" hotkey="g"/>
            <Label value="6p" background="#0096FF" hotkey="h"/>
            <Label value="7p" background="#00B4FF" hotkey="j"/>
            <Label value="8p" background="#00D2FF" hotkey="k"/>
            <Label value="9p" background="#00F0FF" hotkey="l"/>
            <Label value="5pr" background="#FF00FF" hotkey=";"/>
            <Label value="ton" background="#000000" hotkey="z"/>
            <Label value="nan" background="#646464" hotkey="x"/>
            <Label value="sha" background="#969696" hotkey="c"/>
            <Label value="pei" background="#C8C8C8" hotkey="v"/>
            <Label value="hak" background="#FFFFFF" hotkey="b"/>
            <Label value="hat" background="#00FF00" hotkey="n"/>
            <Label value="tyn" background="#FF0000" hotkey="m"/>
        </RectangleLabels>
    </View>
</View>
```
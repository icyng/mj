"""
詳細 : inst.md
"""

from ultralytics import YOLO
import os

from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from mahjong.constants import EAST, SOUTH, WEST, NORTH
import mjpai


def save_file_and_output(results, file_names, class_names):
    '''ファイルと必要なデータの出力'''
    groups = []
    with open("../res/res.txt","w") as o:
        for result,name in zip(results,file_names):
            boxes = result.boxes
            print(f"# result : {name}",file=o)
            hai_set = []
            for box in boxes:
                class_id, confidence, startx = int(box.cls[0]), box.conf[0], box.xyxy[0][0]
                class_name = class_names[class_id]
                hai_set.append({
                    'point':startx,
                    'conf':confidence,
                    'class':class_name})
            hai_set.sort(key=lambda x:x['point'])
            hai_set = mjpai.clean(hai_set)
            groups.append([h['class'] for h in hai_set])
            for h in hai_set:
                print(f"Class: {h['class']}, Confidence: {h['conf']:.3f}",file=o)
            print('\n',file=o)
            result.save(filename=f"../res/r{name}")
    return groups, hai_set

def print_hand_result(hand_result, tehai, wait, hora):
    '''結果出力'''
    print('')
    print(f"@手牌[m,p,s,j] : {tehai}")
    print(f"@待ち牌 : {wait}")
    print(f"@和了牌 : {hora}")
    print(f"@翻数 : {hand_result.han}, 符数 : {hand_result.fu}")
    #点数(ツモアガリの場合[左：親失点, 右:子失点], ロンアガリの場合[左:放銃者失点, 右:0])
    print(f"@失点 : {hand_result.cost['main']}, {hand_result.cost['additional']}")
    print(f"@役 : {hand_result.yaku}")
    print("@符数の詳細 : ")
    for fu_item in hand_result.fu_details:
        print(fu_item)
    print('')

def main():
    folder_path = '../datasets/data_tempai/'
    file_names = os.listdir(folder_path)
    file_pathes = [folder_path+f for f in file_names]

    model = YOLO('best.pt')
    results = model(file_pathes)
    class_names = model.names

    calculator = HandCalculator()
    res, _ = save_file_and_output(results, file_names, class_names)

    # 判定する手牌
    target = res[0] # TODO
    # 待ち牌リスト
    machi_hai = mjpai.machi_hai(target)
    # 和了牌
    hora_hai = '2s' # TODO
    # 聴牌(0向聴)
    old = mjpai.tilemaker(target)
    # 和了形
    new = mjpai.tilemaker(target, add=[hora_hai]) # TODO

    #アガリ形tilesobject(man=マンズ, pin=ピンズ, sou=ソーズ, honors=字牌)
    tiles = TilesConverter.string_to_136_array(man=new[0], pin=new[1], sou=new[2], honors=new[3], has_aka_dora=False) # TODO
    #アガリ牌tilesobject
    win_tile = TilesConverter.string_to_136_array(sou='2')[0] # TODO

    # 鳴き
    melds = None # TODO
    # ドラ(表示牌,裏ドラ)
    dora_indicators = [
        TilesConverter.string_to_136_array(pin='9')[0],
    ] # TODO
    # リーチ、一発、風、ロンorツモ, その他オプションルールや赤ドラなども追加可能
    config = HandConfig(is_riichi=True, player_wind=EAST, round_wind=SOUTH, is_tsumo=False, options=OptionalRules(has_open_tanyao=True, fu_for_open_pinfu=True, fu_for_pinfu_tsumo=True, has_aka_dora=False)) # TODO

    result = calculator.estimate_hand_value(tiles, win_tile, melds, dora_indicators, config)
    print_hand_result(result, old, machi_hai, hora_hai)

if __name__ == '__main__':
    main()

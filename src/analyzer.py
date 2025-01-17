from ultralytics import YOLO
import os

from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.shanten import Shanten
from mahjong.meld import Meld
from mahjong.constants import EAST, SOUTH, WEST, NORTH

class TileRecognizer:
    
    def __init__(
        self,
        result: list[str],
        class_names: list[str]
    ):
        """解析の出力整形

        Args:
            result (list[str]): 単純にmodelに入れた時の認識結果
            class_names (list[int]): クラスの名前リスト
        """
        self.result = result
        self.cls = class_names
        self.hai_dicts = list()
        self.hai_names = list()
        self._out()
    
    def _out(self):
        """牌情報の更新"""
        boxes, hai_d = self.result.boxes, []

        for box in boxes:
            cls_id, conf, startx = int(box.cls[0]), box.conf[0], box.xyxy[0][0]
            cls_name = self.cls[cls_id]
            hai_d.append({
                'class_name': cls_name,
                'confidence': float(conf),
                'point': float(startx)
            })

        self.hai_dicts = self._clean(sorted(hai_d,key=lambda x:x['point']))
        self.hai_names = [h['class_name'] for h in self.hai_dicts]
    
    def _clean(self, hai):
        """重複や精度の低い認識結果を排除

        Args:
            hai (list[dict]): 牌情報

        Returns:
            list[dict]: 牌情報（更新版）
        """
        previous_point, previous_conf, black = hai[0]['point'], 0, []
        hai = [h for h in hai if h['confidence'] > 0.2]

        for i, h in enumerate(hai):
            if abs(h['point'] - previous_point) < 20 / (1 + i):
                if h['confidence'] < previous_conf:
                    black.append(i)
                else:
                    black.append(i - 1)
                    previous_point = h['point']
                    previous_conf = h['confidence']
            else:
                previous_point = h['point']
                previous_conf = h['confidence']

        for index in sorted(black, reverse=True):
            if index >= 0:
                hai.pop(index)
        return hai

class HandAnalyzer:
    sz = {'1s': 1, '2s': 2, '3s': 3, '4s': 4, '5s': 5, '5sr': 0, '6s': 6, '7s': 7, '8s': 8, '9s': 9}
    mz = {'1m': 1, '2m': 2, '3m': 3, '4m': 4, '5m': 5, '5mr': 0, '6m': 6, '7m': 7, '8m': 8, '9m': 9}
    pz = {'1p': 1, '2p': 2, '3p': 3, '4p': 4, '5p': 5, '5pr': 0, '6p': 6, '7p': 7, '8p': 8, '9p': 9}
    hr = {'ton': 1, 'nan': 2, 'sha': 3, 'pei': 4, 'hak': 5, 'hat': 6, 'tyn': 7}
    
    def __init__(self, tiles, hora, has_aka=False, melds=[], doras=[], **kwargs):
        """手牌分析

        Args:
            tiles (list): 認識結果の牌の名称リスト
            hora (str): 上がり牌
            has_aka (bool): 赤があるかどうか
            melds (list): 鳴き牌リスト
            doras (list): ドラリスト
            kwargs: その他オプション
        """
        self.tiles = tiles
        self.hora = hora
        self.has_aka = has_aka
        self.melds = melds
        self.doras = doras
        self.config = self._create_config(**kwargs)
        self.result = self.analyze_hand()
    
    def analyze_hand(self):
        """Analyze hand and calculate results."""
        calculator = HandCalculator()
        
        machi_hai, st = self._machi_hai() # 待ち牌とステ（シャン点数）
        new = self._tilemaker(add=self.hora) # 和了牌を含めた牌リスト
        new_tiles = TilesConverter.string_to_136_array(
            man=new[0],
            pin=new[1],
            sou=new[2],
            honors=new[3],
            has_aka_dora=self.has_aka
        )
        
        #アガリ牌のみのtilesobject
        if self.hora in self.sz: win_tile = TilesConverter.string_to_136_array(sou=str(self.sz[self.hora]))[0]
        elif self.hora in self.mz: win_tile = TilesConverter.string_to_136_array(man=str(self.mz[self.hora]))[0]
        elif self.hora in self.pz: win_tile = TilesConverter.string_to_136_array(pin=str(self.pz[self.hora]))[0]
        elif self.hora in self.hr: win_tile = TilesConverter.string_to_136_array(honors=str(self.hr[self.hora]))[0]
        
        # ドラ(表示牌,裏ドラ)
        dora_indicators = []
        for d in self.doras:
            if d in self.sz: res = TilesConverter.string_to_136_array(sou=str(self.sz[d]))[0]
            elif d in self.mz: res = TilesConverter.string_to_136_array(man=str(self.mz[d]))[0]
            elif d in self.pz: res = TilesConverter.string_to_136_array(pin=str(self.pz[d]))[0]
            elif d in self.hr: res = TilesConverter.string_to_136_array(honors=str(self.hr[d]))[0]
            dora_indicators.append(res)
        
        # 鳴き(ポン・チー・カンも指定)
        # TODO: 未実装、天カメ終了後
        melds = [
            Meld(Meld.KAN, TilesConverter.string_to_136_array(man='2222'), False),
            Meld(Meld.PON, TilesConverter.string_to_136_array(pin='333')),
            Meld(Meld.CHI, TilesConverter.string_to_136_array(sou='567'))
        ]
        result = calculator.estimate_hand_value(new_tiles, win_tile, self.melds, dora_indicators, self.config)
        return new, self.hora, machi_hai, st, result.yaku, result.cost
    
    def _machi_hai(self):
        """待ち牌計算

        Returns:
            machi_list, st: 待ち牌の候補リストとシャン点数を返す
        """
        # 手牌が13枚未満の場合は処理しない
        if len(self.tiles) < 13: return [], '待ち計算できません'
        
        shanten = Shanten()
        config = self._tilemaker()
        config = [c.replace('0','5') for c in config]
        tiles = TilesConverter.string_to_34_array(man=config[0], pin=config[1], sou=config[2], honors=config[3])
        result = shanten.calculate_shanten(tiles)

        if result < 0: st = '和了'
        elif result > 0: st = f'{result}向聴'
        else: st = '聴牌'

        machi_list = []
        for a,_ in (self.sz|self.mz|self.pz|self.hr).items():
            tile = self._tilemaker(add=a)
            tile = [t.replace('0','5') for t in tile]
            tiles = TilesConverter.string_to_34_array(man=tile[0], pin=tile[1], sou=tile[2], honors=tile[3])
            if shanten.calculate_shanten_for_regular_hand(tiles) < 0: machi_list.append(a)
            if shanten.calculate_shanten_for_kokushi_hand(tiles) < 0: machi_list.append(a)
            if shanten.calculate_shanten_for_chiitoitsu_hand(tiles) < 0: machi_list.append(a)
        
        return machi_list, st
    
    def _tilemaker(self, add: str=''):
        """TileConverterの型に沿うようにする

        Args:
            add (str, optional): 通常は和了牌を入力. Defaults to ''.

        Returns:
            [man,pin,sou,honors]: 型に沿うように出力
        """
        man,pin,sou,honors = '','','',''
        for l in self.tiles+[add]:
            if l in self.sz: sou += str(self.sz[l])
            elif l in self.mz: man += str(self.mz[l])
            elif l in self.pz: pin += str(self.pz[l])
            elif l in self.hr: honors += str(self.hr[l])
        return [man,pin,sou,honors]
    
    def _create_config(self, **kwargs):
        """Create hand configuration."""
        return HandConfig(
            is_riichi=kwargs.get('is_riichi', True),
            is_ippatsu=kwargs.get('is_ippatsu', False),
            player_wind=kwargs.get('player_wind', EAST),
            round_wind=kwargs.get('round_wind', SOUTH),
            is_tsumo=kwargs.get('is_tsumo', False),
            is_rinshan=kwargs.get('is_rinshan', False),
            is_chankan=kwargs.get('is_chankan', False),
            is_haitei=kwargs.get('is_haitei', False),
            is_houtei=kwargs.get('is_houtei', False),
            is_daburu_riichi=kwargs.get('is_daburu_riichi', False),
            is_nagashi_mangan=kwargs.get('is_nagashi_mangan', False),
            is_tenhou=kwargs.get('is_tenhou', False),
            is_renhou=kwargs.get('is_renhou', False),
            is_chiihou=kwargs.get('is_chiihou', False),
            is_open_riichi=kwargs.get('is_open_riichi', False),
            kyoutaku_number=kwargs.get('kyoutaku_number', 0),
            tsumi_number=kwargs.get('tsumi_number', 0),
            paarenchan=kwargs.get('paarenchan', 0),
            options=OptionalRules(
                has_open_tanyao=kwargs.get('has_open_tanyao', False),
                has_aka_dora=self.has_aka,
                has_double_yakuman=kwargs.get('has_double_yakuman', False),
                kazoe_limit=HandConfig.KAZOE_LIMITED,
                kiriage=kwargs.get('kiriage', False),
                fu_for_open_pinfu=kwargs.get('fu_for_open_pinfu', False),
                fu_for_pinfu_tsumo=kwargs.get('fu_for_pinfu_tsumo', False),
                renhou_as_yakuman=kwargs.get('renhou_as_yakuman', False),
                has_daisharin=kwargs.get('has_daisharin', False),
                has_daisharin_other_suits=kwargs.get('has_daisharin_other_suits', False),
                has_sashikomi_yakuman=kwargs.get('has_sashikomi_yakuman', False),
                limit_to_sextuple_yakuman=kwargs.get('limit_to_sextuple_yakuman', False),
                paarenchan_needs_yaku=kwargs.get('paarenchan_needs_yaku', False),
                has_daichisei=kwargs.get('has_daichisei', False),
            )
        )
        

def print_hand_result(hand_result, tehai, wait, hora):
    '''結果出力'''
    if not tehai: return
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
    image_path = '../datasets/data_tempai/agari1.png'
    model = YOLO('best.pt')
    result = model(image_path)
    
    # 解析結果
    recognizer = TileRecognizer(result[0], model.names)

    analyzer = HandAnalyzer(
        recognizer.hai_names,
        hora='5p',
        has_aka=False,
        melds=[], 
        doras=['ton','8m','nan'],
        is_riichi=True,
        is_ippatsu=False,
        is_tsumo=True,
        player_wind=WEST,
        round_wind=EAST,
        is_rinshan=False,
        is_chankan=False,
        is_haitei=False,
        is_houtei=False,
        is_daburu_riichi=False,
        is_nagashi_mangan=False,
        is_tenhou=False,
        is_renhou=False,
        is_chiihou=False,
        is_open_riichi=False,
        has_open_tanyao=False,
        has_double_yakuman=False,
        kiriage=False,
        fu_for_open_pinfu=False,
        fu_for_pinfu_tsumo=False,
        renhou_as_yakuman=False,
        has_daisharin=False,
        has_daisharin_other_suits=False,
        has_sashikomi_yakuman=False,
        limit_to_sextuple_yakuman=False,
        paarenchan_needs_yaku=False,
        has_daichisei=False,
        kyoutaku_number=0,
        tsumi_number=0,
        paarenchan=0,
    )

    print(analyzer.result)

if __name__ == '__main__':
    main()

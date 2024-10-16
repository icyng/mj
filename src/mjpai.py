from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter


# 牌に対応する数字をまとめた
sz = {'1s':1,'2s':2,'3s':3,'4s':4,'5s':5,'5sr':0,'6s':6,'7s':7,'8s':8,'9s':9}
mz = {'1m':1,'2m':2,'3m':3,'4m':4,'5m':5,'5mr':0,'6m':6,'7m':7,'8m':8,'9m':9}
pz = {'1p':1,'2p':2,'3p':3,'4p':4,'5p':5,'5pr':0,'6p':6,'7p':7,'8p':8,'9p':9}
hr = {'ton':1,'nan':2,'sha':3,'pei':4,'hak':5,'hat':6,'tyn':7}

# 捨牌
trash = {
    '1s':1,'2s':1,'3s':1,'4s':1,'5s':1,'5sr':0,'6s':1,'7s':1,'8s':1,'9s':1,
    '1m':1,'2m':1,'3m':1,'4m':1,'5m':1,'5mr':0,'6m':1,'7m':1,'8m':1,'9m':1,
    '1p':1,'2p':1,'3p':1,'4p':1,'5p':1,'5pr':0,'6p':1,'7p':1,'8p':1,'9p':1,
    'ton':1,'nan':1,'sha':1,'pei':1,'hak':1,'hat':1,'tyn':1
}

def tilemaker(p: list[str], add: list[str] = []):
    '''TileConverterの型に沿うように出力'''
    man,pin,sou,honors = '','','',''
    for l in p+add:
        if l in sz: sou += str(sz[l])
        elif l in mz: man += str(mz[l])
        elif l in pz: pin += str(pz[l])
        elif l in hr: honors += str(hr[l])
    return [man,pin,sou,honors]


def clean(hai: list[dict]):
    '''
    データ整形

    :param hai: list[{'point':startx, 'conf':confidence, 'class':class_name}]
    :return: list[dict]

    '''
    b, conf, black = hai[0]['point'], 0, []
    # 精度が低すぎるものは排除
    hai = [h for h in hai if h['conf'] > 0.3]
    # 重なっているものは精度が高いものを残す
    for i,h in enumerate(hai):
        if abs(h['point']-b) < 20/(1+i):
            if h['conf'] < conf: 
                black.append(i)
            else:
                black.append(i-1)
                b = h['point']
                conf = h['conf']
        else:
            b = h['point']
            conf = h['conf']
    for index in sorted(black, reverse=True):
        if index >= 0:hai.pop(index)
    return hai


def machi_hai(tehai: list[str]):
    '''13枚の場合のみで検証 (例外処理なし) '''

    shanten = Shanten()

    config = tilemaker(tehai)
    config = [t.replace('0','5') for t in config]
    tiles = TilesConverter.string_to_34_array(man=config[0], pin=config[1], sou=config[2], honors=config[3])
    result = shanten.calculate_shanten(tiles)

    if result < 0: return '和了'
    elif result > 0: return f'{result}向聴'

    machi_list = []
    for a,_ in (sz|mz|pz|hr).items():
        tile = tilemaker(tehai, add=[a])
        tile = [t.replace('0','5') for t in tile]
        tiles = TilesConverter.string_to_34_array(man=tile[0], pin=tile[1], sou=tile[2], honors=tile[3])
        if shanten.calculate_shanten_for_regular_hand(tiles) < 0: machi_list.append(a)
        if shanten.calculate_shanten_for_kokushi_hand(tiles) < 0: machi_list.append(a)
        if shanten.calculate_shanten_for_chiitoitsu_hand(tiles) < 0: machi_list.append(a)
    
    return machi_list
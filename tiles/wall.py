import random
from loguru import logger


class MahjongWall:
    def __init__(self):
        # 初始化 136 张牌
        tiles = []
        for s in ['m', 's', 'p']:
            for n in range(1, 10): tiles.extend([f"{n}{s}"] * 4)
        for n in range(1, 8): tiles.extend([f"{n}z"] * 4)
        
        random.shuffle(tiles)
        self.dead_wall = tiles[-14:]
        self.live_wall = tiles[:-14]
        self.dora_indicators = [self.dead_wall[4]] # 初始翻开第一张宝牌指示牌

    def draw(self):
        return self.live_wall.pop(0) if self.live_wall else None
    
    def get_dora_indicators(self):
        return self.dora_indicators
    
    def run(self):
        """
        一个可自行控制的牌山
        """
        pass
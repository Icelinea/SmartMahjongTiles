import os
import time
from queue import Queue, Empty
import pygame
from loguru import logger

from agent.game import MahjongGame


# 假设之前的 MahjongGame 类已经定义好
# 这里定义一些 UI 常量
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = (50, 70)  # 单张牌的尺寸
BG_COLOR = (34, 139, 34) # 森林绿，模拟麻将桌布，还有 _draw_tile 颜色没全局化


class MahjongUI:
    def __init__(self, mode="debug"):
        pygame.init()
        """
        self._mode: 
        1. "debug": Show all players tiles, no hidden info.
        2. "play": Only show the human player tile.
        """
        self._mode: str = mode
        assert self._mode in ["debug", "play"]

        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python 日本麻将模拟器")
        # self._font = pygame.font.SysFont("SimHei", 24)    # 字体
        self._tile_images = self.load_tile_images()
        self._player_rects = [] # 存储当前玩家手牌的矩形区域，用于碰撞检测

    def _window_safecheck(self, x, y):
        assert x - TILE_SIZE[0] >= 0
        assert x + TILE_SIZE[0] <= SCREEN_WIDTH
        assert y - TILE_SIZE[1] >= 0
        assert y + TILE_SIZE[1] <= SCREEN_HEIGHT

    def _draw_tile(self, x, y, args=[], type=""):
        """
        绘制牌
        type:
        1. back
        2. front
        3. word
        """
        assert type in ["back", "front", "word"]
        # self._window_safecheck(x, y)

        rect = pygame.Rect(x, y, TILE_SIZE[0], TILE_SIZE[1])
        if type == "back":
            pygame.draw.rect(self._screen, (100, 100, 200), rect) # 背面蓝色
        elif type == "front":
            pygame.draw.rect(self._screen, (255, 255, 255), rect) # 正面白色
            # 渲染图片
            img = self._tile_images.get(args[0], self._tile_images.get("back"))
            self._screen.blit(img, (x, y))
        elif type == "word":
            assert False
            pygame.draw.rect(self._screen, (255, 255, 255), rect) # 正面白色
            # text = self._font.render(tile_code, True, (0, 0, 0))
            # self._screen.blit(text, (x + 5, y + 20))
        pygame.draw.rect(self._screen, (0, 0, 0), rect, 2) # 边框
        
    def _render(self, players_hands, discards):
        self._screen.fill(BG_COLOR)
        self._player_rects = [] # 每帧清空，重新计算
        
        # 1. 绘制宝牌指示牌 (Dora)
        # dora_indicator = self.game.wall.get_dora_indicators()
        # self._draw_tile(dora_indicator, SCREEN_WIDTH//2 - 25, 50)
        # dora_label = self._font.render("宝牌指示牌", True, (255, 255, 255))
        # self._screen.blit(dora_label, (SCREEN_WIDTH//2 - 50, 20))

        # 2. 绘制四个玩家的手牌 (简化：下方为自己，其他三家为背面)
        # self._hand_sort(0)
        positions = [
            (200, 580), # 玩家0 (底部)
            (850, 150), # 玩家1 (右侧)
            (200, 50),  # 玩家2 (顶部)
            (50, 150)   # 玩家3 (左侧)
        ]

        player_idx = 0  # extra para
        try:
            # for i in range(len(players_hands)):
            for idx, tile in enumerate(players_hands[0]): # i
                x, y = positions[0]   # i
                offset = idx * (TILE_SIZE[0] + 5)
                mode = "front" if idx == player_idx or self._mode == "debug" else "back"
                rect = pygame.Rect(x + offset, y, TILE_SIZE[0], TILE_SIZE[1])
                
                self._draw_tile(x + offset if 0 % 2 == 0 else x,
                                y if 0 % 2 == 0 else y + idx*30, [tile], mode)
                
                if idx == player_idx:
                    self._player_rects.append((rect, idx))  # 保存矩形和对应的牌索引
        except Exception as e:
            logger.exception(e)

        # 3. 绘制弃牌区 (Discards)
        discard_positions = [(400, 400), (600, 300), (400, 200), (200, 300)]
        for i, discards in enumerate(discards):
            base_x, base_y = discard_positions[i]
            for idx, tile in enumerate(discards):
                row = idx // 6
                col = idx % 6
                self._draw_tile(base_x + col*35, base_y + row*50, [tile], "front")

        pygame.display.flip()

    def _handle_click(self, pos):
        """处理鼠标点击逻辑"""
        # 只有在轮到玩家 0 且手牌为 14 张时才能出牌
        if self.game._turn == 0 and len(self.game._players_hand[0]) == 14:
            for rect, idx in self._player_rects:
                if rect.collidepoint(pos):
                    # 1. 执行出牌逻辑
                    logger.debug(f"idx: {idx}")
                    tile = self.game._players_hand[0].pop(idx)
                    self.game._discards[0].append(tile)
                    # 2. 排序剩余手牌
                    self._hand_sort(0)
                    # 3. 切换回合
                    print(f"玩家 {0} 点击打出了: {tile}")
                    break
        else:
            tile = self.game._players_hand[0].pop()
            self.game._discards[0].append(tile)
            self._hand_sort(0)
            print(f"玩家 {self.game._turn} 点击打出了: {tile}")
        self.game._turn = (self.game._turn + 1) % 4

    @staticmethod
    def load_tile_images():
        """
        预加载所有图片资源
        """
        images = {}
        photo_path = "./resource/regular/"
        suits = ["m", "s", "p", "z"]
        # 加载 1-9m, 1-9s, 1-9p, 1-7z 以及红宝牌 0m, 0s, 0p
        for s in suits:
            nums = range(1, 10) if s != "z" else range(1, 8)
            if s != "z": nums = list(nums) + [0] # 包含红宝牌
            
            for n in nums:
                code = f"{n}{s}"
                path = photo_path + f"{code}.png"
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    # 缩放到设定的大小
                    images[code] = pygame.transform.scale(img, TILE_SIZE)

        # 加载其他图片资源
        if os.path.exists(photo_path + "back.png"):
            images["back"] = pygame.transform.scale(pygame.image.load(photo_path + "back.png"), TILE_SIZE)
        if os.path.exists(photo_path + "front.png"):
            images["back"] = pygame.transform.scale(pygame.image.load(photo_path + "front.png"), TILE_SIZE)
        if os.path.exists(photo_path + "blank.png"):
            images["back"] = pygame.transform.scale(pygame.image.load(photo_path + "blank.png"), TILE_SIZE)

        return images

    def run(self, data_queue: Queue):
        try:
            clock = pygame.time.Clock()
            running = True
            while running:
                # pygame 事件捕获
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    # if event.type == pygame.MOUSEBUTTONDOWN:
                    #     if event.button == 1: # 左键点击
                    #         pass
                    #         self._handle_click(event.pos)

                # game 传递的游戏数据渲染
                try:
                    item = data_queue.get_nowait()
                    if item:
                        self._render(item["players_hands"], item["discards"])

                    if self._mode == "debug":
                        logger.debug(f"--- UI Side ---")
                        logger.debug("players_hands: {}".format(item["players_hands"][0]))
                        logger.debug("discards: {}\n".format(item["discards"][0]))
                except Empty:
                    # get_nowait 未捕获到数据的异常
                    pass

                # 渲染帧率
                clock.tick(60)
        except Exception as e:
            logger.exception(e)
        finally:
            pygame.quit()
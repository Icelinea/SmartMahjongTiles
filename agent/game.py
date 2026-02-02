import time
from copy import deepcopy
from queue import Queue
from loguru import logger

from tiles.wall import MahjongWall


class MahjongGame:
    def __init__(self, heart_beats=60, debug_mode=False):
        self.wall = MahjongWall()
        self._players_hands = [[], [], [], []]
        self._discards = [[], [], [], []] # 弃牌区（河）
        self._turn = 0  # 0:东, 1:南, 2:西, 3:北

        self._heart_beats = heart_beats
        self.debug_mode = debug_mode

    def _setup(self):
        """初始配牌"""
        for i in range(4):
            self._players_hands[i] = [self.wall._live_wall.pop(0) for _ in range(13)]
            self._players_hands[i].sort()

    def _hand_sort(self, idx):
        suit_priority = {"m": 0, "p": 1, "s": 2, "z": 3}
        self._players_hands[idx].sort(key=lambda tile: (suit_priority[tile[1]], int(tile[0])))

    def _run_turn(self, data_queue):
        """运行一个回合：摸牌 -> 思考 -> 打牌"""
        # 1. 摸牌
        new_tile = self.wall.draw()
        if not new_tile: return False # 荒牌平局

        p_idx = self._turn
        if self.debug_mode:
            logger.debug(f"\n--- 【{['东', '南', '西', '北'][p_idx]}家】巡目开始 ---")

        self._hand_sort(p_idx)
        self._players_hands[p_idx].append(new_tile)
        self._data_commit(data_queue)

        if self.debug_mode:
            logger.debug(f"玩家 {p_idx} 摸牌: {new_tile}")
            logger.debug(f"当前手牌: {self._players_hands[p_idx]}")

        # 2. 玩家决策
        discard_tile = self._players_hands[p_idx].pop()
        self._hand_sort(p_idx)

        self._discards[p_idx].append(discard_tile)
        self._data_commit(data_queue)

        if self.debug_mode:
            logger.debug(f"玩家 {p_idx} 打出: {discard_tile}")

        # 3. 切换权到下一位
        self._turn = (self._turn + 1) % 4
        return True
    
    def _data_commit(self, data_queue: Queue):
        item = {
            "players_hands": deepcopy(self._players_hands),
            "discards": deepcopy(self._discards)
        }
        data_queue.put(item)
        time.sleep(1)

    def run(self, data_queue: Queue):
        running = True

        while running:
            running = self._run_turn(data_queue)
        
        if self.debug_mode:
            logger.debug(f"Round Ended.")
            
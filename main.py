
import asyncio
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor

from loguru import logger

from tiles.wall import MahjongWall
from agent.game import MahjongGame
from ui.window import MahjongUI


class SmartMahjong():
    def __init__(self):
        self._tiles = MahjongWall()
        self._game = MahjongGame(debug_mode=True)
        self._ui = MahjongUI(mode="debug", game=self._game)

        self._game._setup()

        self._wall_thread: threading.Thread = threading.Thread(target=self._tiles.run, daemon=True)
        self._game_thread: threading.Thread = threading.Thread(target=self._game.run, daemon=True)
        self._ui_thread: threading.Thread = threading.Thread(target=self._ui.run, daemon=True)
        self._threads = [self._wall_thread, self._game_thread, self._ui_thread]
    
    def run(self):
        # for i in range(len(self._threads)):
            # self._threads[i].start()
        self._threads[2].start()

        try:
            while True:
                time.sleep(1)
        except Exception as e:
            if e == "KeyboardInterrupt":
                logger.exception(f"Threads Killed by Keyboard Interrupt.")
            else:
                logger.exception(e)


async def main():
    try:
        bot = SmartMahjong()
        await bot.run()
    finally:
        logger.info(f"Program Exited.")

if __name__ == "__main__":
    asyncio.run(main())
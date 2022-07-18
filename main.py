"""main module"""

import asyncio
import logging
import sys

from bot import Bot
from utils.config import DockerConfig

# Setup log system
log = logging.getLogger()
log.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S")

# Logger for a file
f = logging.FileHandler("logs/bot.log", "a", encoding="utf-8")
f.setLevel(logging.INFO)
f.setFormatter(formatter)
log.addHandler(f)

# Logger for stdout
screen = logging.StreamHandler(sys.stdout)
screen.setLevel(logging.INFO)
screen.setFormatter(formatter)
log.addHandler(screen)

# Get environment variables (config.ini)
config = DockerConfig("config.ini")

async def main():
    bot = Bot()
    token = config.get_var("DISCORD", "TOKEN")

    await bot.start(token)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
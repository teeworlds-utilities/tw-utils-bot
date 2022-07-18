"""cache module"""

from redis import Redis

from utils.config import DockerConfig

CONFIG = DockerConfig("config.ini")

class Cache(Redis):
    """
        Used to avoid useless asset download
    """

    def __init__(self, db: int=0):
        super().__init__(
            host=CONFIG.get_var("REDIS", "HOST"),
            password=CONFIG.get_var("REDIS", "PASSWORD"),
            port=CONFIG.get_var("REDIS", "PORT"),
            db=db,
            charset="utf-8",
            decode_responses=True
        )

"""configuration module"""

import os

from configparser import ConfigParser, NoSectionError
from sys import stderr
from typing import Any

class DockerConfig(ConfigParser):
    """
        Since docker-compose has no feature to read/write python .ini file,
        this class will be used to catch variables in .ini files or in 
        the environment

        This way, we can pass environment variables throught Docker
        and still using the python config system
    """

    def __init__(self, filename: str):
        self.filename = filename

        super().__init__()
        self.read(filename)

    def get_var(self, section: str, option: str) -> Any:
        """
            Overriding ConfigParser method, it checks for env variables first,
            if there is none, then it takes it from file
        """

        value = os.getenv(section + "_" + option)

        if value:
            return value

        try:
            value = self.get(section, option)
        except NoSectionError as error:
            print(error, file=stderr)

        return value

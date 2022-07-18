"""tw-utils requests module"""

import requests
import json

from utils.config import DockerConfig
from typing import Union, List

config = DockerConfig("config.ini")

class TwUtilsAPI:
    """
        Class used to manage request with the tw-utils  API
    """

    HOST = config.get_var("TW_UTILS", "HOST")
    PORT = config.get_var("TW_UTILS", "PORT")
    HOST = HOST + ":" + PORT

    def request(_type: callable, *args, **kwargs) -> object:
        """
            tw-utils HTTP request
        """

        try:
            req = _type(*args, **kwargs)

            if req.status_code != 200:
                return None

            return req
        except:
            return None

    def common_request(func: callable, route: str, data: json) -> Union[bytes, None]:
        """
            Common tw-utils HTTP request
        """

        req = TwUtilsAPI.request(
            func,
            url=TwUtilsAPI.HOST + route,
            json=data
        )

        if not req:
            return None

        return req.content
    
    def render(data: json) -> Union[bytes, None]:
        """
            Returns a rendered Teeworlds skin
        """

        return TwUtilsAPI.common_request(
            requests.get,
            "/render",
            data
        )

    def render_color(data: json) -> Union[bytes, None]:
        """
            Returns a rendered Teeworlds skin with colors
        """

        return TwUtilsAPI.common_request(
            requests.get,
            "/renderColor",
            data
        )

    def scene(data: json) -> Union[bytes, None]:
        """
            Returns a Teeskins scene
        """

        return TwUtilsAPI.common_request(
            requests.get,
            "/scene",
            data
        )
    
    def scene_list() -> Union[List[str], None]:
        """
            Returns a list of the available scenes
        """

        req = TwUtilsAPI.request(
            requests.get,
            url=TwUtilsAPI.HOST + "/sceneList"
        )

        if not req:
            return None

        return req.json()

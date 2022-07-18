"""asset module"""

from PIL import Image

ASSET_TYPE = {
    "skin": {
        "size": {"w": 256, "h": 128},
        "max_size": {"w": 4096, "h": 2048},
        "divisor": {"w": 8, "h": 4}
    },
    "mapres": {
        "size": {"w": -1, "h": -1},
        "max_size": {"w": 2048, "h": 2048},
        "divisor": {"w": 1, "h": 1}
    },
    "gameskin": {
        "size": {"w": 1024, "h": 512},
        "max_size": {"w": 2048, "h": 1024},
        "divisor": {"w": 8, "h": 4}
    },
    "emoticon": {
        "size": {"w": 512, "h": 512},
        "max_size": {"w": 512, "h": 512},
        "divisor": {"w": 4, "h": 4}
    },
    "entity": {
        "size": {"w": 1024, "h": 1024},
        "max_size": {"w": 1024, "h": 1024},
        "divisor": {"w": 1, "h": 1}
    },
    "cursor": {
        "size": {"w": 512, "h": 512},
        "max_size": {"w": 512, "h": 512},
        "divisor": {"w": 1, "h": 1}
    },
    "particle": {
        "size": {"w": 512, "h": 512},
        "max_size": {"w": 512, "h": 512},
        "divisor": {"w": 8, "h": 8}
    }
}

WRONG_ERROR_MSG = "⚠️ Something went wrong"
NOT_FOUND_ERROR_MSG = "☁️ Nothing has not been found"

def is_asset_valid(_type: str, img: Image) -> bool:
    """
        Check if the asset has a valid size
    """

    data = None

    try:
        data = ASSET_TYPE[_type]
    except KeyError:
        return False
    
    div = data["divisor"]
    size = data["max_size"]

    if img.size[0] % div["w"] or img.size[1] % div["h"]:
        return False
    if data["size"] == {"w": -1, "h": -1}:
        return True
    if img.size[0] > size["w"] or img.size[1] > size["h"]:
        return False

    return True

"""utilities module"""

from sys import stderr
import discord
import os
import pandas as pd

from typing import Dict, Tuple, Any, List

async def basic_message(ctx: object, msg: str, footer: str = None) -> object:
    """
        Sending a simple message    
    """
    
    embed: object = discord.Embed(color=0x000000, description=msg)

    if footer:
        embed.set_footer(text=footer)

    return await ctx.send(embed=embed)

def signature_check(data: bytes, sig: bytes) -> bool:
    """
        Check file signature
    """

    return data[:len(sig)] == sig

def fill_min(*args: Tuple[list]) -> list:
    """
        Set every list with the same length
    """

    length = len(max(*args, key=len))
    args = list(args)
    
    for i in range(len(args)):
        args[i] += (length - len(args[i])) * [" "]

    return args

def make_groups(arr: Any, size: int) -> list:
    """
        Makes list of iterable with a costant size
    """

    return [arr[i:i + size] for i in range(0, len(arr), size)]

async def send_img(
    message: discord.Message,
    name: str,
    filename: str,
    url: str=None
    ):
    """
        Saving a temp image and send it to a Discord channel
    """

    kwargs = {
        "title": name, 
        "color": 0x000000
    }
        
    embed = discord.Embed(**kwargs)
    file = discord.File(filename, filename=filename)

    embed.set_image(url="attachment://" + filename)
    await message.channel.send(embed=embed, file=file)

    os.remove(filename)

def format_find(documents: List[Dict], *keys: Tuple[str]) -> Dict[str, List]:
    """
        Parsing / re-format mongoDB find requests result
    """

    ret = {}

    for document in documents:
        for key in keys:
            if not key in document.keys():
                continue

            value = document[key]

            try:
                ret[key].append(value)
            except KeyError as error:
                # print(error, file=stderr)
                ret[key] = [value]

    return ret

def create_asset_pages(documents: List[Dict]) -> List[List[str]]:
    """
        Generates formatted pages for asset
    """
    
    parsed_docs = format_find(
            documents,
            "_id",
            "assetName",
            "authorName",
            "type"
        )
    frame = pd.DataFrame(parsed_docs).to_string(index=False)
    pages = make_groups(frame.split("\n"), 10)

    return pages

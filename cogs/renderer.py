"""renderer cog"""

import discord
import json
import uuid

from discord.ext import commands
from utils.config import DockerConfig

from utils.utilities import basic_message, send_img
from utils.database import TwUtilsDB
from cogs.apis.twutils import TwUtilsAPI
from cogs.data.asset import WRONG_ERROR_MSG, NOT_FOUND_ERROR_MSG

config = DockerConfig("config.ini")

async def send_render(
    message: discord.message,
    call: callable,
    data: json,
    name: str=None
    ):
    """
        It will send the rendered skin to a Discord channel
    """

    img = call(data)
    url = data["skin"]

    if not img:
        return await basic_message(
            message.channel,
            "❌ Error, invalid skin or invalid command format"
        )

    filename = str(uuid.uuid1()) + ".png"

    with open(filename, "wb") as f:
        f.write(img)
    
    await send_img(message, name, filename, url)

class Renderer(commands.Cog):
    """
        Rendering Teeworlds skins
        (via upload or commands)
    """

    def __init__(self):
        self.db_conn = TwUtilsDB()
    
    async def upload_handler(self, message: discord.Message):
        """
            Rendering uploaded valid skins
        """

        attachs = message.attachments

        if len(attachs) != 1:
            return

        attach = attachs[0]

        if (not ".png" in attach.filename):
            return

        url = attachs[0].url
        data = {"skin": url}

        await send_render(message, TwUtilsAPI.render, data)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
            Listening for skin upload
        """

        if message.channel.name != "skin-rendering":
            return

        await self.upload_handler(message)

    @commands.command(aliases=["render"])
    async def r(
        self,
        ctx: commands.Context,
        skin_id: str=None,
        eye: str=None
    ):
        """
            Render a skin from skins.tw with an id
        """

        if not skin_id:
            return

        res = self.db_conn.get_accepted_asset_by_id(
            skin_id,
            str(ctx.guild.id)
        )

        if not res:
            return await basic_message(
                ctx,
                NOT_FOUND_ERROR_MSG
            )

        data = {
            "skin": res["path"],
            "eye": eye or "default_eye"
        }

        await send_render(ctx, TwUtilsAPI.render, data, res["assetName"])
    
    @commands.command(aliases=["rendercolor"])
    async def rc(
        self,
        ctx: commands.Context,
        skin_id: str=None,
        bcolor: str=None,
        fcolor: str=None,
        mode: str=None,
        eye: str=None
    ):
        """
            Render a skin with color from skins.tw with an id
        """

        if not skin_id or not bcolor or not fcolor or not mode:
            return

        res = self.db_conn.get_accepted_asset_by_id(
            skin_id,
            str(ctx.guild.id)
        )

        if not res:
            return await basic_message(
                ctx,
                NOT_FOUND_ERROR_MSG
            )

        data = {
            "skin": res["path"],
            "bcolor": bcolor,
            "fcolor": fcolor,
            "mode": mode,
            "eye": eye or "default_eye"
        }

        await send_render(ctx, TwUtilsAPI.render_color, data, res["assetName"])

def setup(bot: commands.Bot):
    bot.add_cog(Renderer())

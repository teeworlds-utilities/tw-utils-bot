"""scene cog"""

import uuid

from discord.ext import commands
from typing import List, Dict

from cogs.apis.twutils import TwUtilsAPI
from cogs.data.asset import (
    WRONG_ERROR_MSG,
    NOT_FOUND_ERROR_MSG
)
from utils.page import Pages
from utils.database import TwUtilsDB
from utils.utilities import (
    send_img,
    basic_message,
    make_groups
)

class Scene(commands.Cog, Pages):
    """
        Managing the scenes system
    """

    def __init__(self):
        Pages.__init__(self)

        self.db_conn = TwUtilsDB()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if not reaction.message.author.bot or user.bot:
            return

        await reaction.remove(user)
        await self.handler(reaction, user)

    @commands.command()
    async def scene(
        self,
        ctx: commands.Context,
        name: str=None,
        skin_id: str=None
        ):
        """
            Displays a Teeskins scene, with an optional tee
        """

        if not name or not skin_id:
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
            "name": name,
            "skin": res["path"]
        }

        img = TwUtilsAPI.scene(data)

        if not img:
            return await basic_message(
                ctx,
                WRONG_ERROR_MSG
            )

        filename = str(uuid.uuid1()) + ".png"

        with open(filename, "wb") as f:
            f.write(img)
    
        await send_img(ctx, name, filename)

    @commands.command()
    async def scenes(self, ctx: commands.Context):
        """
            List the availables scene
        """

        scenes = TwUtilsAPI.scene_list()

        if not scenes:
            return

        page_content = make_groups(scenes, 10)

        await self.create_pages(ctx, page_content)

def setup(bot: commands.Bot):
    bot.add_cog(Scene())

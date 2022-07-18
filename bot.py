"""Overriding commands.Bot"""

import discord
import logging

from typing import *
from discord.ext import commands

from utils.config import DockerConfig
from utils.database import TwUtilsDB

log = logging.getLogger(__name__)
config = DockerConfig("config.ini")

EXTENSIONS = (
    "cogs.asset",
    "cogs.renderer",
    "cogs.scene",
)

commands.MinimalHelpCommand()
class Bot(commands.Bot, TwUtilsDB):
    """
        Primary class that contains the bot object to run
    """

    def __init__(self):
        self.bot_options = {}

        self._get_options()
        super().__init__(**self.bot_options)

        # Init MongoDB database, colections and apply schemas
        self.conn = TwUtilsDB()

        for extension in EXTENSIONS:
            # try:
            self.load_extension(extension)
            log.info(f"Loaded the extension {extension}")
            # except:
                # log.warning(f"Failed to load the extension {extension}")

    def _get_options(self):
        for k, v in config.items("BOT"):
            k = k.lower()
            if (v):
                self.bot_options[k] = eval(v)

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Game(name = "tw-utils"))

    async def close(self):
        log.critical("Closing")
        await self.close()

    async def on_command(self, ctx: commands.Context):
        dest = [f"#{ctx.channel} ({ctx.guild})", "DM"][not ctx.guild]
        log.info(f"{ctx.author} used command in {dest}: {ctx.message.content}")

    async def on_guild_join(self, guild: discord.Guild):
        log.warning(f"{self.user} (ID: {self.user.id}) has joined {guild.name} (ID: {guild.id})")

        self.conn.add_guild(
            {
                "guildID": str(guild.id)
            }
        )

    async def on_guild_remove(self, guild: discord.Guild):
        log.warning(f"{self.user} (ID: {self.user.id}) has left {guild.name} (ID: {guild.id})")

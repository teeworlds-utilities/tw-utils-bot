"""upload cog"""

import hashlib
import uuid
import requests
import discord
import io
import os

from discord.ext import commands
from typing import Dict
from PIL import Image
from datetime import datetime

from utils.config import DockerConfig
from utils.utilities import (
    basic_message,
    create_asset_pages,
    signature_check,
)
from utils.database import TwUtilsDB
from utils.cache import Cache
from cogs.data.asset import (
    ASSET_TYPE,
    WRONG_ERROR_MSG,
    NOT_FOUND_ERROR_MSG,
    is_asset_valid
)
from utils.page import Pages

config = DockerConfig("config.ini")
unique_key = lambda ctx: str(ctx.guild.id) + str(ctx.author.id)

STORAGE_PATH = config.get_var("STORAGE", "PATH")

class UserPreUpload:
    """
        Represents upload informations before its uploaded (only PNGs)
    """

    def __init__(
        self,
        ctx: commands.Context,
        bot_msg: commands.Context,
        **data: Dict[str, str]
        ):

        self.ctx = ctx
        self.bot_msg = bot_msg
        self.data = data or {}
    
    def __getitem__(self, __name: str) -> str:
        """
            Returns an attr in self.data
        """

        if not __name in self.data.keys():
            return ""
        
        return self.data[__name]
    
    def fancy_footer(self) -> str:
        """
            Returns a fancy string about the upload provider
        """

        ret = "📥 The *%s* `%s` by `%s` has been added to the waiting queue" % \
            (
                self["type"],
                self["name"],
                self["author"]
            )

        return ret
    
    def fill_data(self, **extra_data: Dict[str, str]):
        """
            Fills the class data attr after the user uploaded the image
        """

        self.data = {
            **self.data,
            **extra_data
        }

class UserPreUploads:
    """
        This class manages multiple UserUpload
    """

    def __init__(self):
        self.pre_uploads = {}

    def __getitem__(self, key: str) -> UserPreUpload:
        if not key in self.pre_uploads.keys():
            return None
        
        return self.pre_uploads[key]

    def add(self, ctx: commands.Context,
        bot_msg: commands.Context,
        **data: Dict[str, str]
        ) -> bool:
        """
            Add a UserPreUpload object to the pre_uploads dict
        """

        key = unique_key(ctx)

        if self[key]:
            return False

        self.pre_uploads[key] = UserPreUpload(ctx, bot_msg, **data)

        return True
    
    def remove(self, key: str):
        """
            Removes an UserPreUpload from self.pre_uploads
        """

        del self.pre_uploads[key]

class Asset(commands.Cog, Pages):
    """
        It manages the uploads from Discord guilds
    """

    CANCEL_MSG: str = "To reset your upload details: !t cancel"

    def __init__(self, bot: commands.Bot) -> None:
        self.users_pre_upload = UserPreUploads()
        self.db_conn = TwUtilsDB()
        self.cache = Cache()
        Pages.__init__(self)

        self.bot = bot

    async def upload_asset(
        self,
        key: str,
        message: object,
        asset: object,
        pre_upload: UserPreUpload
        ):
        """
            Uploading asset to the Teeskins waiting queue
            (where administrators have to accept the skins)
        """

        # Set up the document
        fields = {
            "assetName": pre_upload["name"],
            "type": pre_upload["type"],
            "path": pre_upload["path"],
            "checksum": pre_upload["checksum"],
            "guildID": str(message.guild.id),
            "authorID": str(message.author.id),
            "authorName": pre_upload["author"],
            "createdAt": datetime.now(),
            "accepted": False
        }

        res = self.db_conn.add_to_queue(fields)

        await message.delete()
        await pre_upload.bot_msg.delete()

        # Check if the document has been inserted to the collection
        if not res:
            return await basic_message(
                message.channel,
                "❌ Your asset has not been uploaded"
            )

        await basic_message(
            message.channel,
            pre_upload.fancy_footer(),
            f"id: {res.inserted_id}"
        )

         # Save the bytes (asset content) as file
        if not os.path.exists(fields["path"]):
            with open(fields["path"], "wb") as f:
                f.write(asset.content)

        self.users_pre_upload.remove(key)

    async def upload_handler(self, message: object):
        """
            It manages Discord attachments for assets
        """
    
        # 1. Checking if the attachment is valid
        attachs = message.attachments

        if len(attachs) != 1:
            return
        
        key = unique_key(message)
        pre_upload = self.users_pre_upload[key]

        if message.author.bot or not pre_upload:
            return

        if not pre_upload.ctx.channel.id == message.channel.id:
            return

        # 2. Download the asset and check if its a PNG
        asset = requests.get(attachs[0])
        if not signature_check(
            asset.content,
            b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
        ):
            return await basic_message(
                message.channel,
                "❌ Only PNGs are supported"
            )
        
        # 3 Check the size
        img = Image.open(io.BytesIO(asset.content))
        if not is_asset_valid(pre_upload.data["type"], img):
            return await basic_message(
                message.channel,
                "❌ Invalid asset"
            )

        # 4. Check if it already exists in the same guild
        checksum = hashlib.md5(asset.content).hexdigest()
        duplicate = self.db_conn.duplicate(
            checksum, str(message.guild.id)
        )

        if duplicate:
            return await basic_message(
                message.channel,
                f"❌ This asset has already been added to the queue",
                self.CANCEL_MSG
            )
        
        # 5. Try to get the path from the cache

        cached_path = self.cache.get(checksum)

        if not cached_path:
            path = f"{STORAGE_PATH}/{uuid.uuid4()}.png"
            self.cache.set(checksum, path)
        else:
            path = cached_path

        # 6. Additional img metadatas, path, etc...
        pre_upload.fill_data(
            checksum=checksum,
            path=path
        )

        # 7. Try to upload it
        await self.upload_asset(key, message, asset, pre_upload)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if not reaction.message.author.bot or user.bot:
            return

        await reaction.remove(user)
        await self.handler(reaction, user)

    @commands.Cog.listener()
    async def on_message(self, message: object):
        """
            Waiting for users upload
        """

        await self.upload_handler(message)

    @commands.command()
    async def upload(
        self,
        ctx: commands.Context,
        name: str = None,
        _type: str = None,
        author: str = None
        ):
        """
            Upload an asset
            Allowed types:
                skin
                mapres
                gameskin
                emoticon
                entity
                cursor
                particle

            example:
                `tw upload twinbop skin Nagi`
                If you want to use spaces :
                    `tw upload "honk honk" mapres "Nagi01 {LAN}"`
        """

        if not name or not _type or not author:
            return
        if isinstance(ctx.channel, discord.DMChannel):
            return
        if ctx.channel.name != "upload":
            return
        if not _type in ASSET_TYPE.keys():
            return await basic_message(
                ctx,
                "❌ Wrong asset type",
                "check the upload help page (tw help upload)"
            )

        key = unique_key(ctx)
    
        await ctx.message.delete()

        if self.users_pre_upload[key]:
            return await basic_message(
                ctx,
                "🔒 you already have an upload in progress",
                self.CANCEL_MSG
            )
        
        msg = await basic_message(
            ctx, 
            "📌 Your next attachment in this channel will be considered your asset",
            self.CANCEL_MSG
        )

        self.users_pre_upload.add(
            ctx,
            msg,
            name=name, type=_type, author=author
        )

    async def asset_view(
        self,
        channel: commands.Context,
        data: dict
    ):
        """
            Send a discord.Embed object with the asset informations
            If error, the object will contains an error message
        """

        filename = data["assetName"] + ".png"
        embed = discord.Embed(
            title=data["assetName"],
            description=data["_id"],
            color=0x000000
        )
        uploader = await self.bot.fetch_user(data["authorID"])

        embed.set_image(url="attachment://" + filename)
        embed.set_footer(text=f"Uploaded by {uploader} and created by {data['authorName']} on {str(data['createdAt'])[:-7]}")

        msg = await channel.send(
            embed=embed,
            file=discord.File(
                data["path"],
                filename=filename
            )
        )

        self.db_conn.link_msg_id(
            data["_id"],
            str(msg.id),
            str(channel.id)
        )

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def inspect(self, ctx: commands.Context, _id: str=None):
        """
            Allow to administrators to load any asset
        """

        if not _id:
            return
        
        res = self.db_conn.get_guild_asset_by_id(_id, str(ctx.guild.id))

        if not res:
            return await basic_message(
                ctx,
                NOT_FOUND_ERROR_MSG
            )
        
        await self.asset_view(ctx.channel, res)

    @commands.command()
    async def cancel(self, ctx: commands.Context):
        """
            Cancel the user upload in progress
        """

        key = unique_key(ctx)

        if not self.users_pre_upload[key]:
            return

        self.users_pre_upload.remove(key)
        await basic_message(
            ctx,
            "🔓 Your current upload has been canceled"
        )

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def accept(self, ctx: commands.Context, _id: str=None):
        """
            Accept asset in the waiting queue
        """

        if not _id:
            return

        await ctx.message.delete()

        res = self.db_conn.accept(_id, str(ctx.guild.id))

        if not res:
            return await basic_message(
                ctx,
                "❌ This asset is not in the queue"
            )
        
        channels = self.db_conn.get_channels(
            str(ctx.guild.id),
            res["type"]
        )

        if not channels or channels[res["type"]] == "current":
            channel = ctx.channel
        else:
            channel = channels[res["type"]]
            channel = self.bot.get_channel(int(channel))
        
        await self.asset_view(channel, res)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def remove(self, ctx: commands.Context, _id: str=None):
        """
            Remove an asset of the guild
        """

        if not _id:
            return

        await ctx.message.delete()

        res = self.db_conn.remove_asset_by_id(_id, str(ctx.guild.id))

        if not res:
            return await basic_message(
                ctx,
                WRONG_ERROR_MSG
            )
        
        await basic_message(
            ctx,
            f"🔥 You removed `{_id}` from this guild"
        )
        
        checksum = res["checksum"]
        on_other_guild = self.db_conn.find_by_checksum(checksum)

        if on_other_guild:
            return

        self.cache.delete(checksum)
        os.remove(res["path"])

        try:
            channel = self.bot.get_channel(int(res["discord_channel_id"]))
            msg = await channel.fetch_message(res["discord_msg_id"])

            await msg.delete()
        except Exception as error:
            return

    @commands.command()
    async def findall(self, ctx: commands.Context, _type: str=None):
        """
            Find every guild's assets by type
        """

        if not _type:
            return

        res = self.db_conn.get_assets_by_type(
            str(ctx.guild.id),
            _type
        )

        if not res:
            return await basic_message(
                ctx,
                NOT_FOUND_ERROR_MSG
            )
        
        pages = create_asset_pages(res)
        await self.create_pages(ctx, pages)

    @commands.command()
    async def findname(self, ctx: commands.Context, name: str=None):
        """
            Find every guild's assets containing "name" in their name
        """

        if not name:
            return

        res = self.db_conn.get_assets_contain_name(
            str(ctx.guild.id),
            name
        )

        if not res:
            return await basic_message(
                ctx,
                NOT_FOUND_ERROR_MSG
            )
    
        pages = create_asset_pages(res)
        await self.create_pages(ctx, pages)
    
    @commands.command()
    async def load(self, ctx: commands.Context, _id: str=None):
        """
            Upload asset by a specific id       
        """

        if not _id:
            return
        
        res = self.db_conn.get_accepted_asset_by_id(_id, str(ctx.guild.id))

        if not res:
            return await basic_message(
                ctx,
                NOT_FOUND_ERROR_MSG
            )
        
        await self.asset_view(ctx.channel, res)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def queue(self, ctx: commands.Context):
        """
            Upload asset by a specific id       
        """

        res = self.db_conn.get_queue(str(ctx.guild.id))

        if not res:
            return await basic_message(
                ctx,
                NOT_FOUND_ERROR_MSG
            )
        
        pages = create_asset_pages(res)
        await self.create_pages(ctx, pages)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def setchannel(
        self,
        ctx: commands.Context,
        category: str=None,
        channel_id: str=None
    ):
        """
            Link a channel id with a category
        """

        if not category or not channel_id:
            return
        
        if not category in ASSET_TYPE.keys():
            return await basic_message(
                ctx,
                "❌ Wrong asset type",
                "check the upload help page (tw help upload)"
            )
        
        if not channel_id in map(lambda x: str(x.id), ctx.guild.text_channels):
            return await basic_message(
                ctx,
                "❌ Unauthorized channel"
            )

        res = self.db_conn.set_channel(
            str(ctx.guild.id),
            channel_id,
            category
        )

        if not res:
            return await basic_message(
                ctx,
                WRONG_ERROR_MSG
            )

        channel = self.bot.get_channel(int(channel_id))

        if not channel:
            return await basic_message(
                ctx,
                WRONG_ERROR_MSG
            )

        await basic_message(
            ctx,
            f"👏 You linked `{category}` with {channel.mention}"
        )

def setup(bot: commands.Bot):
    bot.add_cog(Asset(bot))

"""pages manager"""

import discord

from typing import Any, List, Union
from discord.ext import commands

from utils.binds import Binds
from utils.reactions import Reactions, PageReaction
from utils.utilities import make_groups

class Page:
    """
        This object represents a page and stores
        useful informations to interact with the Discord message
    """

    def __init__(
            self,
            message: commands.Context,
            author_id: int,
            content: List[List[str]],
            lines_per_page: int = 10
        ):
        self.message = message
        self.author_id = author_id
        self.content = content
        self.lines_per_page = lines_per_page
        self.index = 0

    def set_content(self, content: List[str]):
        """
            Sets self.content and formats it
        """

        self.content = make_groups(content, self.lines_per_page)

    def set_index(self, index: int) -> bool:
        """
            Updates the page index
        """

        if index < 0:
            return False
        if index >= len(self.content):
            return False
        
        self.index = index

        return True

    def move(self, n: int) -> bool:
        """
            Moves index of n pages        
        """

        return self.set_index(self.index + n)
    
    async def edit(self):
        """
            Edits the Discord message
        """

        page_str_content = "\n".join(self.content[self.index])

        msg = "```" + page_str_content + "\n" + \
        f"page {self.index + 1} / {len(self.content)}" + "```"
    
        await self.message.edit(content=msg)

    async def delete(self):
        """
            Deletes the Discord message and the object
        """

        await self.message.delete()
        del self

class Pages(Binds):
    """
        Manages Page objects
    """

    def __init__(self):
        super().__init__()

        self.pages = {}
        self.init()

    def init(self):
        """
            Initializes binds
        """
    
        self.add_bind(str(Reactions.PREVIOUS), self.move_page, n=-1)
        self.add_bind(str(Reactions.NEXT), self.move_page, n=1)
        self.add_bind(str(Reactions.DELETE), self.delete_page)
    
    def add_page(self, message: discord.Message, author_id: str, pages: List[str]) -> Page:
        """
            Adds a Page to the dictionnary
        """

        ret = Page(message, author_id, pages)
        self.pages[message.id] = ret

        return ret

    async def create_pages(self, ctx: commands.Context, pages: List[List[str]]):
        """
            Creates and sends a page message
        """

        msg = "```" + '\n'.join(pages[0]) + "\n" + \
        f"page 1 / {len(pages)}" + "```"

        message = await ctx.send(msg)
        for _, v in PageReaction.__members__.items():
            await message.add_reaction(v.value)

        self.add_page(message, ctx.author.id, pages)

    def get_good_page(self, reaction: object, user: object) -> Union[Page, None]:
        """
            Returns a Page if the user has clicked on a binded emoji and if it
            is his message, otherwise it returns None
        """

        message_id = reaction.message.id

        if not str(reaction) in self.key_binding.keys():
            return None
        if not message_id in self.pages.keys():
            return None

        page = self.pages[message_id]
        if page.author_id != user.id:
            return None

        return page

    async def move_page(self, page: Page, n: int):
        """
            Moves the page
        """

        if not page.move(n):
            return
        await page.edit()

    async def delete_page(self, page: Page):
        """
            Deletes the page
        """

        await page.delete()

    async def handler(self, reaction: object, user: object):
        """
            Calls functions if needed
        """

        page = self.get_good_page(reaction, user)

        if not page:
            return

        await self.try_call_from_bind(str(reaction), page=page)

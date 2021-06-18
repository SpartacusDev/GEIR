from discord.ext import commands, menus
from discord import Message, Embed
import requests


class Packages(menus.Menu):
    def new(self, packages: list):
        self.packages = packages
        self.message = None
        self.current_page = 0
        return self

    async def send_initial_message(self, ctx, channel):
        self.message = await channel.send(embed=self.create_embed())
        return self.message
    
    def create_embed(self, page: int=0) -> Embed:
        embed_message = Embed(title=self.packages[page]["name"], color=0xff0000)
        embed_message.add_field(name="Package Identifier", value=self.packages[page]["package"])
        embed_message.add_field(name="Version", value=self.packages[page]["version"])
        embed_message.add_field(name="Maintainer", value=self.packages[page]["maintainer"])
        embed_message.add_field(name="Description", value=self.packages[page]["description"])
        embed_message.add_field(name="Dependencies", value=f"{', '.join([f'`{dependency}`' for dependency in self.packages[page]['dependencies']])}")
        embed_message.add_field(name="Free/Paid", value="Free" if self.packages[page]["free"] else "Paid")
        embed_message.add_field(name="Repo URL", value=self.packages[page]["repo"])
        embed_message.add_field(name="Section", value=self.packages[page]["section"] if not self.packages[page]["section"] == "" else "Unknown")
        embed_message.add_field(name="Tags", value=f"{', '.join([f'`{tag}`' for tag in self.packages[page]['tag']])}" if not self.packages[page]["tag"] == [] else "_ _")
        embed_message.add_field(name="Author", value=self.packages[page]["author"])
        embed_message.set_thumbnail(url=self.packages[page]["icon"])
        embed_message.set_author(name="Download", url=self.packages[page]["filename"])
        return embed_message
    
    @menus.button("⬅️")
    async def previous_page(self, payload):
        if self.current_page - 1 >= 0:
            self.current_page -= 1
            await self.message.edit(embed=self.create_embed(self.current_page))
        else:
            self.current_page = len(self.packages) - 1
            await self.message.edit(embed=self.create_embed(self.current_page))

    @menus.button("➡️")
    async def next_page(self, payload):
        if self.current_page + 1 < len(self.packages):
            self.current_page += 1
            await self.message.edit(embed=self.create_embed(self.current_page))
        else:
            self.current_page = 0
            await self.message.edit(embed=self.create_embed(self.current_page))


class Tweaks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.command(description="Searches tweak in out API! Example: `*search AppSync Unified`")
    async def search(self, ctx: commands.Context):
        query = ctx.message.content[len(f"{self.bot.command_prefix(self.bot, ctx.message)}search ") : ]
        if query == "":
            await ctx.send("Please provide a valid query.")
            return
        data = self._search(query)
        pages = Packages().new(data["data"])
        await pages.start(ctx)
    
    @staticmethod
    def _search(query):
        response = requests.get(f"https://spartacusdev.herokuapp.com/api/search/{query}")
        data = response.json()
        return data
    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot or len(message.content) == 0:
            return
        is_triggered = self._trigger(message.content)
        if is_triggered is False:
            return
        query = message.content[is_triggered[0] : is_triggered[1]].lower()
        data = self._search(query)
        if data == []:
            await message.channel.send("Tweak not found.")
            return
        first_result = data["data"][0]
        embed_message = Embed(
            title=first_result["name"],
            color=0xff0000
        )
        embed_message.add_field(name="Package Identifier", value=first_result["package"])
        embed_message.add_field(name="Version", value=first_result["version"])
        embed_message.add_field(name="Maintainer", value=first_result["maintainer"])
        embed_message.add_field(name="Description", value=first_result["description"])
        embed_message.add_field(name="Dependencies", value=f"{', '.join([f'`{dependency}`' for dependency in first_result['dependencies']])}")
        embed_message.add_field(name="Free/Paid", value="Free" if first_result["free"] else "Paid")
        embed_message.add_field(name="Repo URL", value=first_result["repo"])
        embed_message.add_field(name="Section", value=first_result["section"] if not first_result["section"] == "" else "Unknown")
        embed_message.add_field(name="Tags", value=f"{', '.join([f'`{tag}`' for tag in first_result['tag']])}" if not first_result["tag"] == [] else "_ _")
        embed_message.add_field(name="Author", value=first_result["author"])
        embed_message.set_thumbnail(url=first_result["icon"])
        embed_message.set_author(name="Download", url=first_result["filename"])
        await message.channel.send(embed=embed_message)
    
    def _trigger(self, message: str):
        if "[[" not in message or "]]" not in message \
            or message.index("[[") > message.index("]]"):
            return False
        
        return message.index("[[") + 2, message.index("]]")

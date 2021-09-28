from discord.ext import commands
from discord.utils import get
from discord import Embed, Guild
from .database import Prefix, db


class Other(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.command(
        description="Show this message."
    )
    @commands.guild_only()
    async def help(self, ctx: commands.Context):
        embed_message = Embed(title="Help", color=0xff0000)
        [embed_message.add_field(name=command.name, value=command.description) for command in self.bot.commands]
        embed_message.set_footer(text="Support server: https://discord.gg/PVqz3x4", icon_url=self.bot.get_guild(778314788199071745).icon_url)
        await ctx.send(embed=embed_message)
    
    @commands.command(
        description="Get an invite link for the bot."
    )
    async def invite(self, ctx: commands.Context):
        await ctx.send("https://discord.com/api/oauth2/authorize?client_id=736195692858441758&permissions=8&scope=bot")
    
    @commands.command(
        description="Gives the role of the device"
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def give_role(self, ctx: commands.Context, device: str=None):
        if device is None:
            await ctx.send("Please provide a valid device identifier.")
            return
        role = get(ctx.guild.roles, name=device)
        if role is None:
            await ctx.send("Role not found.")
            return
        if role in ctx.author.roles:
            try:
                await ctx.author.remove_roles(role)
            except:
                await ctx.send(f"Falied to remove your {device} role")
            else:
                await ctx.send(f"Removed your {device} role!")
            return
        try:
            await ctx.author.add_roles(role)
        except:
            await ctx.send(f"Failed to add you the {device} role")
        else:
            await ctx.send(f"Added you the {device} role!")
    
    @commands.command(
        description="Blacklist/whitelist the server so GEIR won't/will create any more roles"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def blacklist(self, ctx: commands.Context):
        prefix = db.query(Prefix).filter(Prefix.guild_id == f"{ctx.guild.id}").first()
        if prefix is None:
            prefix = Prefix(guild_id = f"{ctx.guild.id}", prefix="*", blacklisted=True)
            db.add(prefix)
            db.commit()
            await ctx.send("I won't be creating any more roles in this server")
            return
        if prefix.blacklisted is None:
            prefix.blacklisted = True
        else:
            prefix.blacklisted = not prefix.blacklisted
        db.commit()
        await ctx.send(f"I {'won\'t' if prefix.blacklisted else 'will'} be creating any more roles in this server")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        prefix = Prefix(guild_id=f"{guild.id}", prefix="*")
        db.add(prefix)
        db.commit()
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild):
        db.delete(db.query(Prefix).filter(Prefix.guild_id == f"{guild.id}").first())
        db.commit()
    
    @commands.command(description="Change the bot's prefix")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx: commands.Context):
        new_prefix = ctx.message.content[len(f"{self.bot.command_prefix(self.bot, ctx.message)}prefix ") : ]
        if new_prefix == "":
            await ctx.send("Please provide a valid prefix.")
            return
        prefix = db.query(Prefix).filter(Prefix.guild_id == f"{ctx.guild.id}").first()
        prefix.prefix = new_prefix
        db.commit()
        await ctx.send(f"Changed the prefix to `{prefix.prefix}` successfully!")

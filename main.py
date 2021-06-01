from discord.ext import commands
from discord import Intents, Message
from commands import setup, db, Prefix
import os


TOKEN = os.getenv("BOT_TOKEN")
intents = Intents.default()
intents.members = True
intents.webhooks = True

def command_prefix(bot: commands.Bot, message: Message):
    prefix = db.query(Prefix).filter(Prefix.guild_id == f"{message.guild.id}").first()
    if prefix is None:
        db.add(Prefix(guild_id=f"{message.guild.id}", prefix="*"))
        db.commit()
        return "*"
    return prefix.prefix


bot = commands.Bot(command_prefix=command_prefix, intents=intents, help_command=None)
setup(bot)


if __name__ == "__main__":
    bot.run(TOKEN)
from .other import *
from .tweaks import *
from .ios_announcements import *
from .database import db, Prefix


def setup(bot):
    print("Starting to load cogs...")
    print("---------------------------")

    print("Loading `Tweaks`...")
    try:
        bot.add_cog(Tweaks(bot))
    except:
        print("!Failed to load `Tweaks`!")
    else:
        print("Loaded `Tweaks` successfully!")
    print("Loading `Other`...")
    try:
        bot.add_cog(Other(bot))
    except:
        print("!Failed to load `Other`!")
    else:
        print("Loaded `Other` successfully!")
    print("Loading `Announcements`...")
    try:
        bot.add_cog(Announcements(bot))
    except:
        print("!Failed to load `Announcements`!")
    else:
        print("Loaded `Announcements` successfully!")
    
    print("---------------------------")
    print("All Cogs have been loaded!")

    @bot.event
    async def on_ready():
        print(f"{bot.user} has successfully connected to Discord!")

        print("Starting to check for updates...")
        bot.get_cog("Announcements").check_for_updates.start()
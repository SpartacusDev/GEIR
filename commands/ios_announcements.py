from discord.errors import HTTPException
from discord.ext import commands, tasks, menus
from discord.utils import get
from discord import Embed, Webhook, Role, TextChannel, RawReactionActionEvent
import requests
from .database import db, Device, Prefix


# class Info(menus.Menu):
#     def new(self, firmwares: list):
#         self.firmwares = firmwares
#         self.template = Embed(title="{}", color=0xff0000)
#         self.template.add_field(name="")
#         return self
    
#     def _generate_embed(self, information: dict, page: int=0) -> Embed:
#         embed_message = Embed(title=information["name"], color=0xff0000)
#         embed_message.add_field(name="Identifier", value=information["identifier"])
#         embed_message.add_field(name="Version", value=self.firmwares[0]["version"])
#         embed_message.add_field(name="")
#         ...

#     async def send_initial_message(self, ctx, channel):
#         return await channel.send(embed=)
    
#     @menus.button("⬅️")
#     async def previous_page(self, payload):
#         if not self.can_move:
#             return
#         if self.current_page - 1 >= 0:
#             self.current_page -= 1
#             await self.message.edit(embed=self.api.results[self.current_page].embed)
#         else:
#             self.current_page = len(self.pages) - 1
#             await self.message.edit(embed=self.api.results[self.current_page].embed)

#     @menus.button("➡️")
#     async def next_page(self, payload):
#         if not self.can_move:
#             return
#         if self.current_page + 1 < len(self.api.results):
#             self.current_page += 1
#             await self.message.edit(embed=self.api.results[self.current_page].embed)
#         else:
#             self.current_page = 0
#             await self.message.edit(embed=self.api.results[self.current_page].embed)
    
#     @menus.button("ℹ️")
#     async def information(self, payload):
#         if not self.can_move:
#             return
#         package = self.api.results[self.current_page].package
#         await self.message.edit(embed=package.embed)
#         self.can_move = False
    
#     @menus.button("➕")
#     async def more(self, payload):
#         if not self.can_move:
#             return
#         self.api.next_page()


class List(menus.Menu):
    def new(self, embeds: list):
        self.embeds: list = embeds
        self.current_page: int = 0
        return self

    async def send_initial_message(self, ctx: commands.Context, channel: TextChannel):
        return await channel.send(embed=self.embeds[0])
    
    @menus.button("⬅️")
    async def previous_page(self, payload: RawReactionActionEvent):
        self.current_page -= 1
        if self.current_page < 0:
            self.current_page = len(self.embeds) - 1
        await self.message.edit(embed=self.embeds[self.current_page])

    @menus.button("➡️")
    async def next_page(self, payload: RawReactionActionEvent):
        self.current_page += 1
        if self.current_page == len(self.embeds):
            self.current_page = 0
        await self.message.edit(embed=self.embeds[self.current_page])


class Announcements(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        
        q = db.query(Device)
        for device in q:
            break
        else:
            response = requests.get("https://api.ipsw.me/v2.1/firmwares.json")
            data = response.json()
            devices = data["devices"]
            for device in devices:
                device_obj = Device(device_id=device, signed_versions=self._get_signed_versions_for_device(devices[device]))
                db.add(device_obj)
            db.commit()

        self.new_devices = []
    
    @commands.command(
        description="Show information about the chosen device."
    )
    async def info(self, ctx: commands.Context, device: str=None):
        if device is None:
            await ctx.send(f"Please provide a valid device.\nExample for proper usage of the command: `{self.bot.command_prefix(self.bot, ctx.message)}ipsw iPhone1,1`.")
            return
        response = requests.get(f"https://api.ipsw.me/v4/device/{device}")
        if not response.status_code == 200:
            await ctx.send(f"Please provide a valid device.\nExample for proper usage of the command: `{self.bot.command_prefix(self.bot, ctx.message)}ipsw iPhone1,1`.")
            return
        data = response.json()
        firmwares = self._get_signed_versions_for_device(data)
        embed_message = Embed(title=data["name"], color=0xff0000)
        embed_message.add_field(name="Identifier", value=data["identifier"])
        embed_message.add_field(name="Signed Versions", value=", ".join([f"[{firmware['version']}]({firmware['url']})" for firmware in firmwares]))
        embed_message.add_field(name="Board Configuration", value=data["boardconfig"]) if not data["boardconfig"] == "" else ...
        await ctx.send(embed=embed_message)
    
    @commands.command(
        description="Setup an announcements channel for me."
    )
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.guild_only()
    async def setup(self, ctx: commands.Context, channel: TextChannel=None):
        if channel is None:
            await ctx.send("Please mention a valid text channel.")
            return
        if get(await channel.webhooks(), name="GEIR") is not None:
            await ctx.send(f"I already have a webhook in {channel.mention}!")
            return
        try:
            await channel.create_webhook(name="GEIR", avatar=requests.get(self.bot.user.avatar_url).content)
        except:
            await ctx.send("Failed to create a webhook. Please try again later.")
            return
        await ctx.send("Bot is set up!")
    
    @commands.command(
        description="Remove my announcements channel"
    )
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.guild_only()
    async def remove(self, ctx: commands.Context, channel: TextChannel=None):
        if channel is None:
            await ctx.send("Please mention a valid text channel.")
            return
        webhook = get(await channel.webhooks(), name="GEIR")
        if webhook is None:
            await ctx.send(f"I already don't have a webhook in {channel.mention}!")
            return
        try:
            await webhook.delete()
        except:
            await ctx.send("Failed to create a webhook. Please try again later.")
            return
        await ctx.send(f"{channel.mention} is no longer a GEIR announcements channel!")
    
    @tasks.loop(minutes=10)
    async def check_for_updates(self):
        response = requests.get("https://api.ipsw.me/v2.1/firmwares.json")
        try:
            data = response.json()
        except Exception as e:
            print(f"Failed to check to updates. Error message: {e}")
            return
        devices = data["devices"]

        for device in devices:
            device_obj = db.query(Device).filter(Device.device_id == device).first()
            if device_obj is None:
                self.new_devices.append(device)
                device_obj = Device(device_id=device, signed_versions=self._get_signed_versions_for_device(devices[device]))
                db.add(device_obj)
            else:
                signed_versions = self._get_signed_versions_for_device(devices[device])
                if not signed_versions == device_obj.signed_versions:
                    new_versions = [version for version in signed_versions if version not in device_obj.signed_versions]
                    if len(new_versions) > 0:
                        await self._announce_new_versions(device, new_versions)
                    
                    not_signed_versions = [version for version in device_obj.signed_versions if version not in signed_versions]
                    if len(not_signed_versions) > 0:
                        await self._announce_unsigned_versions(device, not_signed_versions)
                
                    device_obj.signed_versions = signed_versions
            db.commit()  # So it won't say the same thing over and over again when there's an error
            
        # db.commit()
        
        if len(self.new_devices) > 0:
            await self._announce_new_devices()

    def _get_signed_versions(self, devices: list) -> dict:
        signed_dict = {}
        for device in devices:
            signed_dict[device] = self._get_signed_versions_for_device(devices[device])
        return signed_dict
    
    @staticmethod
    def _get_signed_versions_for_device(device: dict) -> list:
        signed = []
        for version in device["firmwares"]:
            if version["signed"]:
                signed.append(version)
        return signed

    async def _announce_new_devices(self):
        for guild in self.bot.guilds:
            if get(guild.members, id=self.bot.user.id).guild_permissions.manage_roles == True:
                prefix = db.query(Prefix).filter(Prefix.guild_id == f"{guild.id}").first()
                if prefix is None or prefix.blacklisted is None:
                    blacklisted = False
                else:
                    blacklisted = prefix.blacklisted
                if not blacklisted:
                    for device in self.new_devices:
                        try:
                            await guild.create_role(name=device)
                        except HTTPException:
                            break
            try:
                webhook: Webhook = get(await guild.webhooks(), name="GEIR")
            except:
                ...
            else:
                if webhook is not None:
                    message = '\n'.join(self.new_devices)
                    await webhook.send(f"New devices has been released:\n{message}")
        self.new_devices = []
    
    async def _announce_new_versions(self, device: str, versions: list):
        for guild in self.bot.guilds:
            if get(guild.members, id=self.bot.user.id).guild_permissions.manage_roles == True:
                prefix = db.query(Prefix).filter(Prefix.guild_id == f"{guild.id}").first()
                if prefix is None or prefix.blacklisted is None:
                    blacklisted = False
                else:
                    blacklisted = prefix.blacklisted
                if not blacklisted:
                    for device in self.new_devices:
                        try:
                            await guild.create_role(name=device)
                        except HTTPException:
                            break
            try:
                webhook: Webhook = get(await guild.webhooks(), name="GEIR")
            except:
                ...
            else:
                try:
                    role = get(guild.roles, name=device)
                    if role is not None:
                        role = role.mention
                except:
                    role = f"@{device}"
                if webhook is not None:
                    message = '\n'.join([version['version'] + ' build ID: ' + version['buildid'] for version in versions])
                    await webhook.send(f"New versions has been released for {role if role is not None else device}:\n{message}")
    
    async def _announce_unsigned_versions(self, device: str, versions: list):
        for guild in self.bot.guilds:
            if get(guild.members, id=self.bot.user.id).guild_permissions.manage_roles == True:
                prefix = db.query(Prefix).filter(Prefix.guild_id == f"{guild.id}").first()
                if prefix is None or prefix.blacklisted is None:
                    blacklisted = False
                else:
                    blacklisted = prefix.blacklisted
                if not blacklisted:
                    for device in self.new_devices:
                        try:
                            await guild.create_role(name=device)
                        except HTTPException:
                            break
            try:
                webhook: Webhook = get(await guild.webhooks(), name="GEIR")
            except:
                ...
            else:
                try:
                    role = get(guild.roles, name=device)
                    if role is not None:
                        role = role.mention
                except:
                    role = f"@{device}"
                if webhook is not None:
                    message = '\n'.join([version['version'] + ' build ID: ' + version['buildid'] for version in versions])
                    await webhook.send(f"Versions that are now unsigned for {role if role is not None else device}:\n{message}")
    
    @commands.command(name="list", description="Shows a list of the compatible devices")
    async def devices_list(self, ctx: commands.Context):
        response = requests.get("https://api.ipsw.me/v4/devices")
        data = response.json()
        page_num = 1
        embeds = []
        embed = Embed(title=f"Page {page_num}", color=0xff0000)
        embed.set_footer(text="Data provided by ipsw.me")
        for device in data:
            if len(embed.fields) == 24:
                page_num += 1
                embeds.append(embed)
                embed = Embed(title=f"Page {page_num}", color=0xff0000)
                embed.set_footer(text="Data provided by ipsw.me")
            embed.add_field(name=f"**Device Name: {device['name']}**", value=f"Device ID: {device['identifier']}")
        if len(embeds) < page_num:
            embeds.append(embed)
        menu = List().new(embeds)
        await menu.start(ctx)

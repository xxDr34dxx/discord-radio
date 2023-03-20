#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Built-in Modules
from datetime import datetime
import time
import logging

# Third Party Modules
import discord
from discord import app_commands
from discord import FFmpegPCMAudio
from discord.utils import get

# Custom Modules
from config import config

__author__ = "dr34d a.k.a. Tori"
__copyright__ = "Copyright 2023, dr34d"
__license__ = "MIT"
__version__ = "2.0.0"
__date__ = "2023-03-20"
__maintainer__ = "dr34d"
__status__ = "Production"

########################## Editable Defaults #########################
# NOTE: Changing these could affect execution in unpredictable ways! #
######################################################################
STATIONS = {
    # A Maximum of 24 stations should be listed at one time
    "DefCon Radio": "https://ice4.somafm.com/defcon-128-mp3",
    "Lush": "https://ice6.somafm.com/lush-128-mp3",
    "Beat Blender": "https://ice4.somafm.com/beatblender-128-mp3",
    "The Trip": "https://ice4.somafm.com/thetrip-128-mp3",
    "PopTron": "https://ice2.somafm.com/poptron-128-mp3",
    "Fluid": "https://ice2.somafm.com/fluid-128-mp3",
    "Black Rock FM": "https://ice6.somafm.com/brfm-128-mp3",
    "Secret Agent": "https://ice2.somafm.com/secretagent-128-mp3",
    "Groove Salad": "https://ice2.somafm.com/groovesalad-128-mp3",
    "Synphaera": "https://ice6.somafm.com/synphaera-128-mp3",
    "Drone Zone": "https://ice6.somafm.com/dronezone-128-mp3",
    "Dark Zone": "https://ice1.somafm.com/darkzone-128-mp3",
    "Metal": "https://ice6.somafm.com/metal-128-mp3",
    "Suburbs of GOA": "https://ice2.somafm.com/suburbsofgoa-128-mp3",
    "Covers": "https://ice6.somafm.com/covers-128-mp3",
    "Cliq Hop": "https://ice6.somafm.com/cliqhop-128-mp3",
    "Dubstep": "https://ice4.somafm.com/dubstep-128-mp3",
    "Deep Space One": "https://ice6.somafm.com/deepspaceone-128-mp3",
    "Space Station": "https://ice6.somafm.com/spacestation-128-mp3",
    "N5MD": "https://ice6.somafm.com/n5md-128-mp3",
    "Vaporwaves": "https://ice2.somafm.com/vaporwaves-128-mp3",
    "Sonic Universe": "https://ice4.somafm.com/sonicuniverse-128-mp3",
    "Mission Control": "https://ice4.somafm.com/missioncontrol-128-mp3",
    #"Digitalis": "https://ice2.somafm.com/digitalis-128-mp3",
    "Move Da House": "https://uk7.internet-radio.com/proxy/movedahouse?mp=/stream",
}
TIMEFORMAT = '%H:%M:%S UTC on %m/%d/%Y'

######################################################################
#############/ / / / DO NOT EDIT BELOW THIS LINE \ \ \ \##############
######################################################################
_log = logging.getLogger('discord.music_bot')
_log.setLevel(logging.INFO)

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)

TIMESTAMP = datetime.now().strftime(TIMEFORMAT)
NOWPLAYING = None
VCHANNELNAME = None
BOTNAME = None
GUILDNAME = None
player = None

@tree.command(name="menu", description="Provides station selection menu", guild=discord.Object(id=config.GUILDID))
async def menu(interaction):
    class StationSelectView(discord.ui.View):
        _log.debug(f"Entered StationSelectView")
        station = None

        @discord.ui.select(
            placeholder="Select a station",
            options=[discord.SelectOption(label=label, value=label) for label in STATIONS]
        )
        async def select_station(self, interaction : discord.Interaction, select_item : discord.ui.Select):
            _log.debug(f"Entered select_station()")
            global NOWPLAYING

            self.station = select_item.values[0]
            NOWPLAYING = STATIONS[self.station]
            self.children[0].placeholder = self.station
            self.children[0].disabled = True
            await interaction.response.edit_message(view=self)
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=self.station))
            _log.info(f"{interaction.user.name} began streaming {self.station} in {VCHANNELNAME} on {GUILDNAME}")
            await play(NOWPLAYING)

    menu = StationSelectView()
    await interaction.response.send_message(view=menu, ephemeral=True)

@tree.command(name="stop", description=f"Stops the player", guild=discord.Object(id=config.GUILDID))
async def stop(interaction):
    global player

    _log.debug(f"Entered stop()")
    player.stop()
    await player.disconnect()
    await interaction.response.send_message("Playback Stopped", ephemeral=True)
    _log.info(f"Playback stopped in {VCHANNELNAME} on {GUILDNAME} by {interaction.user.name}")


async def play(url):
    _log.debug(f"Entered play()")
    global player

    guild = client.get_guild(config.GUILDID)
    channel = discord.utils.get(guild.voice_channels, name=VCHANNELNAME)

    if player is not None:
        _log.debug(f"Player isn't None")
        player.stop()
    else:
        _log.debug(f"Player is None, creating player object...")
        _log.debug(f"VCHANNELNAME = {repr(VCHANNELNAME)}, guild = {guild}, url = {url}")
        _log.debug(f"channel = {repr(channel)}")
        player = await channel.connect()
        _log.debug(f"player = {repr(player)}")
        _log.debug(f"Player connected, attempting to start stream at {url}...")
    player.play(FFmpegPCMAudio(url))
    _log.debug(f"Player started with URL: {url}")

@client.event
async def on_ready():
    _log.debug(f"Entered on_ready()")
    global BOTNAME
    global GUILDNAME
    global VCHANNELNAME

    guild = discord.utils.get(client.guilds, id=config.GUILDID)
    if guild is not None:
        GUILDNAME = guild.name
        _log.debug(f"Guild is {guild.name}")
        BOTNAME = client.user.name
        _log.debug(f"Bot name set to {BOTNAME}")
        channel = get(client.get_all_channels(), id=int(config.VCHANNEL))
        VCHANNELNAME = channel.name
        _log.debug(f"Voice Channel set to {VCHANNELNAME}")
    else:
        _log.critical(f"Guild is None")
        _log.error(f"Could not find guild with the ID: {config.GUILDID}")
    _log.debug(f"Syncing command tree...")
    await tree.sync(guild=discord.Object(id=config.GUILDID))
    _log.debug(f"Command tree synced")
    _log.info(f"{BOTNAME} successfully connected to {GUILDNAME}")

client.run(config.BOT_TOKEN)

from discord.ext import commands
import discord
from cogs.utils import checks
import logging

description = """
A Discord bot written by alepers.
"""

logging.basicConfig(level=logging.INFO)

if not discord.opus.is_loaded():
    script_path = os.path.dirname(os.path.abspath(__file__))
    opus_path = os.path.join(script_path, 'lib', 'opus', 'libopus-0.x64.dll')
    discord.opus.load_opus(opus_path)

prefix = ['!', '?']
bot = commands.Bot(command_prefix=prefix, description=description)

@bot.event
async def on_ready():
    print('Logged in as:')
    print('Username: ' + bot.user.name)
    print('ID: ' + bot.user.id)
    print('------')

@bot.event
async def on_resumed():
    print('resumed...')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

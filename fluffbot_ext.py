from discord.ext import commands
import discord
from cogs.utils import checks
import logging
import json
import os
import aiohttp
import asyncio

description = """
A Discord bot written by alepers.
"""
extensions = [
    'cogs.cog'
]

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

    for server in bot.servers:
        channel = discord.utils.find(lambda c: c.is_default, server.channels)
        await bot.send_message(channel, 'Bleep bloop, I am a robot.')

@bot.event
async def on_resumed():
    print('resumed...')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)

def init_streams():
    with open(os.path.join('input', 'streams.txt'), 'r') as file:
        stream_names = file.readlines()
        stream_names = [x.strip('\n') for x in stream_names]
        stream_statuses = []
        for stream_name in stream_names:
            stream_statuses.append((stream_name, False))
        return dict(stream_statuses)

async def poll_twitch():
    await asyncio.sleep(20)

    if not hasattr(bot, 'streams'):
        bot.streams = init_streams()

    while not bot.is_closed:
        for server in bot.servers:
            channel = discord.utils.find(lambda c: c.is_default, server.channels)
            for user, online in bot.streams.items():
                try:
                    url = 'https://api.twitch.tv/kraken/streams/' + user
                    headers = {'Client-Id': twitch_client_id}
                    info = ''

                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers) as response:
                            info = await response.json()

                    if info['stream'] == None:
                        if online:
                            bot.streams[user] = False
                    else:
                        if not online:
                            bot.streams[user] = True
                            await bot.send_message(channel, user + ' just started streaming! https://www.twitch.tv/' + user)
                except:
                    pass

        await asyncio.sleep(60)

async def auto_join():
    await asyncio.sleep(15)
    while not bot.is_closed:
        for server in bot.servers:
            voice_channels = list(filter(lambda c: c.type == discord.ChannelType.voice and
                c != server.afk_channel and not
                bot.user in c.voice_members, server.channels))
            voice_channels.sort(key=lambda vc: len(vc.voice_members))
            candidate = voice_channels.pop()
            if not bot.is_voice_connected(server):
                await bot.join_voice_channel(candidate)
            else:
                if len(bot.voice_client_in(server).channel.voice_members) - 1 < len(candidate.voice_members):
                    await bot.voice_client_in(server).move_to(candidate)

        await asyncio.sleep(10)

if __name__ == '__main__':
    credentials = load_credentials()
    twitch_client_id = credentials['twitch_client_id']

    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    try:
        bot.loop.create_task(auto_join())
        bot.loop.create_task(poll_twitch())
        bot.loop.run_until_complete(bot.start(credentials['token']))
    except KeyboardInterrupt:
        bot.loop.run_until_complete(bot.logout())
        pending = asyncio.Task.all_tasks()
        gathered = asyncio.gather(*pending)
        try:
            gathered.cancel()
            bot.loop.run_forever()
            gathered.exception()
        except:
            pass
    finally:
        bot.loop.close()

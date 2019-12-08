from discord.ext import commands
import discord
from cogs.utils import checks
import logging
import json
import os
import aiohttp
import asyncio
import sys
import traceback

description = """
A Discord bot written by alepers.
"""
extensions = [
    'cogs.cog_rewrite'
]

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

if not discord.opus.is_loaded():
    script_path = os.path.dirname(os.path.abspath(__file__))
    opus_path = os.path.join(script_path, 'lib', 'opus', 'libopus-0.x64.dll')
    discord.opus.load_opus(opus_path)

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!', '?'), 
                   description=description,
                   case_insensitive=True)


@bot.event
async def on_ready():
    print('Logged in as:')
    print('Username: ' + bot.user.name)
    print('ID: ' + str(bot.user.id))
    print('------')


@bot.event
async def on_resumed():
    print('resumed...')


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, exception):
    if hasattr(ctx.command, 'on_error'):
        return

    cog = ctx.cog
    if cog:
        attr = '_{0.__class__.__name__}__error'.format(cog)
        if hasattr(cog, attr):
            return

    if isinstance(exception, commands.CommandOnCooldown):
        await ctx.message.add_reaction('\N{STOPWATCH}')
        return

    if isinstance(exception, commands.CheckFailure):
        await ctx.message.add_reaction('\N{CROSS MARK}')
        return

    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


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

    while not bot.is_closed():
        for guild in bot.guilds:
            channel = discord.utils.find(lambda c: c.name == "general", guild.channels)

            if channel:
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
                                await channel.send(user + ' just started streaming! https://www.twitch.tv/' + user)
                    except:
                        pass

        await asyncio.sleep(60)


async def auto_join():
    await asyncio.sleep(15)
    while not bot.is_closed():
        for guild in bot.guilds:
            voice_channels = list(filter(lambda c: isinstance(c, discord.VoiceChannel)
                                                   and c != guild.afk_channel
                                                   and not bot.user in c.members,
                                         guild.channels))
            voice_channels.sort(key=lambda c: len(c.members))
            candidate = voice_channels.pop()
            connected_client = discord.utils.find(lambda vc: vc.guild == guild, bot.voice_clients)
            if not connected_client:
                await candidate.connect()
            else:
                if connected_client.channel != candidate:
                    if len(connected_client.channel.members) - 1 < len(candidate.members):
                        await connected_client.move_to(candidate)

        await asyncio.sleep(10)


def main():
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


if __name__ == '__main__':
    main()

import discord
import asyncio
import logging
import ast

from urllib.request import urlopen
from urllib.error import URLError
import json

logging.basicConfig(level=logging.INFO)

if not discord.opus.is_loaded():
    discord.opus.load_opus(r"C:\Users\Alexander\git\FluffBot\lib\opus\libopus-0.dll")

class Bot(discord.Client):
    def init_streams(self):
        with open(r'input\streams.txt', 'r') as file:
            stream_names = file.readlines()
            stream_names = [x.strip('\n') for x in stream_names]
            stream_statuses = []
            for stream_name in stream_names:
                stream_statuses.append((stream_name, False))
            return dict(stream_statuses)

    def __init__(self):
        super().__init__()
        self.player  = None
        self.streams = self.init_streams()
        self.server = list(self.servers)[0]

    def is_playing(self):
        return self.player is not None and self.player.is_playing()

    def go_live(self, user):
        self.streams[user] = True

    def go_offline(self, user):
        self.streams[user] = False

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.is_private:
            await self.send_message(message.channel, 'You cannot use this bot in private messages.')

        elif message.content.startswith('$join'):
            channel_name = message.content[5:].strip()
            check = lambda c: c.name == channel_name and c.type == discord.ChannelType.voice
            channel = discord.utils.find(check, message.server.channels)
            if channel is None:
                await self.send_message(message.channel, 'Cannot find a voice channel by that name.')
            else:
                if self.is_voice_connected(self.server):
                    await self.voice.disconnect()
                await self.join_voice_channel(channel)

        elif message.content.startswith('$leave'):
            if self.is_voice_connected(self.server):
                await self.voice.disconnect()

        elif message.content.startswith('!'):
            if self.player is not None and self.player.is_playing():
                return

            if not self.is_voice_connected(self.server):
                await self.send_message(message.channel, 'Not connected to a voice channel.')
                return

            if not message.author.voice.voice_channel == bot.voice.voice_channel:
                await.self.send_message(message.channel, 'You need to be in this voice channel to play audio.')
                return

            command = message.content[1:len(message.content)]
            with open(r'input\audio.txt', 'r') as audio_handle:
                s = audio_handle.read()
                dic = ast.literal_eval(s)
                if command in dic:
                    self.player = self.voice.create_ffmpeg_player('audio\\' + dic[command])
                    self.player.start()
                else:
                    await self.send_message(message.channel, 'No such command. Type ?help for a list of commands.')

        elif message.content.startswith('?help'):
            help_string = 'Bot commands: '
            with open(r'input\audio.txt', 'r') as audio_handle:
                s = audio_handle.read()
                dic = ast.literal_eval(s)
                for command in dic.keys()
                    help_string += '!' + command + ', '
                help_string = help_string[:len(help_string) - 2]
                await self.send_message(message.channel, help_string)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

async def poll_twitch():
    await bot.wait_until_ready()
    channel = discord.Object(id=discord.utils.find(lambda m: m.name == 'general', bot.server.channels).id)
    while not bot.is_closed:
        for user, online in bot.streams.items():
            try:
                info = json.loads(urlopen('https://api.twitch.tv/kraken/streams/' + user).read().decode('utf-8'))
                if info['stream'] == None:
                    if online:
                        bot.go_offline(user)
                else:
                    if not online:
                        bot.go_live(user)
                        await bot.send_message(channel, user + ' just started streaming! https://www.twitch.tv/' + user)
            except:
                pass
            
        await asyncio.sleep(60)

async def auto_join():
    await bot.wait_until_ready()
    voice_channels = list(filter(lambda c: c.type == ChannelType.voice, bot.server.channels))
    voice_channels.sort(key=lambda vc: len(vc.voice_members))
    candidate = voice_channels.pop()
    if (not bot.is_voice_connected(bot.server) or not 
            len(list(filter(lambda vc: len(vc.voice_members) 
            == len(candidate.voice_members), voice_channels))) > 0):
        await bot.join_voice_channel(candidate)
    
    await asyncio.sleep(10)

login_token = ''

with open(r'input\token.txt', 'r') as token:
    login_token = token.readline().replace('\n', '')

bot = Bot()
try:
    bot.loop.create_task(auto_join())
    bot.loop.create_task(poll_twitch())
    bot.loop.run_until_complete(bot.start(login_token))
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

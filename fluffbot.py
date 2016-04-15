import discord
import asyncio
import logging

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

        elif message.content.startswith('!join'):
            channel_name = message.content[5:].strip()
            check = lambda c: c.name == channel_name and c.type == discord.ChannelType.voice
            channel = discord.utils.find(check, message.server.channels)
            if channel is None:
                await self.send_message(message.channel, 'Cannot find a voice channel by that name.')
            else:
                if self.is_voice_connected():
                	await self.voice.disconnect()
                await self.join_voice_channel(channel)

        elif message.content.startswith('!leave'):
            if self.is_voice_connected():
            	await self.voice.disconnect()

        elif message.content.startswith('!tadetlugnt'):
        	if self.player is not None and self.player.is_playing():
        		return

        	if not self.is_voice_connected():
                    await self.send_message(message.channel, 'Not connected to a voice channel.')
                    return

        	self.player = self.voice.create_ffmpeg_player(r'audio\ta_det_lugnt.mp3')
        	self.player.start()

        elif message.content.startswith('!brainpower'):
        	if self.player is not None and self.player.is_playing():
        		return

        	if not self.is_voice_connected():
                    await self.send_message(message.channel, 'Not connected to a voice channel.')
                    return

        	self.player = self.voice.create_ffmpeg_player(r'audio\brain_power_adj.mp3')
        	self.player.start()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

async def poll_twitch():
	await bot.wait_until_ready()
	channel = discord.Object(id=discord.utils.find(lambda m: m.name == 'general', list(bot.servers)[0].channels).id)
	while not bot.is_closed:
		for user, online in bot.streams.items():
			info = json.loads(urlopen('https://api.twitch.tv/kraken/streams/' + user).read().decode('utf-8'))
			if info['stream'] == None:
				if online:
					bot.go_offline(user)
			else:
				if not online:
					bot.go_live(user)
					await bot.send_message(channel, user + ' just started streaming! https://www.twitch.tv/' + user)
		await asyncio.sleep(60)

email, password = '', ''

with open(r'input\token.txt', 'r') as token:
	email = token.readline().replace('\n', '')
	password = token.readline().replace('\n', '')

bot = Bot()
try:
	bot.loop.create_task(poll_twitch())
	bot.loop.run_until_complete(bot.start(email, password))
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

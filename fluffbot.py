import discord
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

if not discord.opus.is_loaded():
	discord.opus.load_opus(r"C:\Users\Alexander\git\FluffBot\lib\opus\libopus-0.dll")

class Bot(discord.Client):
    def __init__(self):
        super().__init__()
        self.player  = None

    def is_playing(self):
        return self.player is not None and self.player.is_playing()

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

        elif message.content.startswith('!gustavpower'):
        	if self.player is not None and self.player.is_playing():
        		return

        	if not self.is_voice_connected():
                    await self.send_message(message.channel, 'Not connected to a voice channel.')
                    return

        	self.player = self.voice.create_ffmpeg_player(r'audio\gustav_power.mp3')
        	self.player.start()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')


email, password = '', ''

with open(r'input\token.txt', 'r') as token:
	email = token.readline().replace('\n', '')
	password = token.readline().replace('\n', '')

bot = Bot()
bot.run(email, password)
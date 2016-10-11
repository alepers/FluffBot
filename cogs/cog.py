from discord.ext import commands
from .utils import checks
import discord
import inspect
import datetime
import random
import ast

class Cog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def debug(self, ctx, *, code : str):
        """Lets the bot owner evaluate arbitrary code."""

        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.server,
            'channel': ctx.message.channel,
            'author': ctx.message.author
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await self.bot.say(python.format(result))

    @commands.command(pass_context=True)
    async def roll(self, ctx):
        """Rolls for a number between 0-100."""

        minimum = 0
        maximum = 100

        await self.bot.say('{} rolls {}.'.format(ctx.message.author.mention, random.randint(minimum, maximum)))

    @commands.command(pass_context=True)
    async def play(self, ctx, *, audio : str):
        """Plays a specified sound clip. Use 'play help' to see a list of clips."""

        if not hasattr(self.bot, 'player'):
            self.bot.player = None

        if self.bot.player is not None and self.bot.player.is_playing():
            return

        if not self.bot.is_voice_connected(ctx.message.server):
            await self.bot.say('Not connected to a voice channel.')
            return

        if not ctx.message.author.voice.voice_channel == self.bot.voice_client_in(ctx.message.server).channel:
            await self.bot.say('You need to be in this voice channel to play audio.')
            return

        with open(r'input\audio.txt', 'r') as audio_handle:
            s = audio_handle.read()
            dic = ast.literal_eval(s)
            if audio == 'help':
                await self.bot.say('Audio clips: `' + ', '.join(dic.keys()) + '`')
                return

            if audio in dic:
                self.bot.player = self.bot.voice_client_in(ctx.message.server).create_ffmpeg_player('audio\\' + dic[audio])
                self.bot.player.start()
            else:
                await self.bot.say('No such audio clip. Type `!play help` for a list of clips.')

def setup(bot):
    bot.add_cog(Cog(bot))

from discord.ext import commands
from .utils import checks_rewrite
import discord
import asyncio
import inspect
import datetime
import random
import ast
import os


class BotCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(hidden=True)
    @checks_rewrite.is_owner()
    async def debug(self, ctx, *, code : str):
        """Lets the bot owner evaluate arbitrary code."""

        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))
            return

        await ctx.send(python.format(result))


    @commands.command()
    async def roll(self, ctx):
        """Rolls for a number between 0-100."""

        minimum = 0
        maximum = 100

        await ctx.send('{} rolls {}.'.format(ctx.author.mention, random.randint(minimum, maximum)))


    @commands.command()
    async def play(self, ctx, *, audio : str):
        """Plays a specified sound clip. Use 'play help' to see a list of clips."""

        bot_vc = discord.utils.find(lambda vc: vc.guild == ctx.guild, self.bot.voice_clients)
        if not bot_vc or not bot_vc.is_connected():
            await ctx.send('I am not connected to a voice channel yet, hold on..')
            return

        if bot_vc.is_playing():
            return

        if ctx.author.voice:
            if not ctx.author.voice.channel == bot_vc.channel:
                await ctx.send('You need to be in this voice channel to play audio.')
                return

        audio_lowercase = audio.lower()
        with open(os.path.join('input', 'audio.txt'), 'r') as audio_fd:
            content = audio_fd.read()
            audio_dict = ast.literal_eval(content)
            if audio_lowercase == 'help':
                await ctx.send('Audio clips: `' + ', '.join(sorted(audio_dict.keys())) + '`')
                return

            if audio_lowercase in audio_dict:
                bot_vc.play(discord.FFmpegPCMAudio(os.path.join('audio', audio_dict[audio_lowercase])))

                # Clean up play command message
                await asyncio.sleep(2)
                await ctx.message.delete()
            else:
                await ctx.send('No such audio clip. Type `!play help` for a list of clips.')


    @commands.command()
    @commands.cooldown(1, 60.0, type=commands.BucketType.channel)
    async def source(self, ctx):
        """Displays a link to the FluffBot source code on GitHub."""

        await ctx.send('FluffBot source code: https://github.com/alepers/FluffBot')


def setup(bot):
    bot.add_cog(BotCommands(bot))

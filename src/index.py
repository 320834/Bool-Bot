import discord
from discord.ext import commands
import os 
from settings import DISCORD_API_KEY

# Features
import example_feature

# Use bot commands extension. 
# Tutorial: https://discordpy.readthedocs.io/en/latest/ext/commands/index.html
# API: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#bot

# Bot is subclass of client. Any coroutines that defines an event should be usable under bot.
bot = commands.Bot(command_prefix='!')

# ================================================================================
# Bot Configuration
bot.description = ""

# ================================================================================
# Events. 

@bot.event
async def on_ready():
    """
    Coroutine event. Invoked when bot starts up
    """
    print('Logged on as {0}!'.format(bot.user.name))

@bot.event
async def on_message(message):
    """
    Coroutine event. Invoked when user 
    """
    result = await bot.process_commands(message)

    # Ensure no feedback loop.
    if message.author.name != bot.user.name:
        await example_feature.send_mess(message)
    

# ================================================================================
# Commands

@bot.command(name="test")
async def say(ctx, arg):
    """
    Test bot command. Type !test "Message here"
    """
    await ctx.send(arg)


bot.run(DISCORD_API_KEY)
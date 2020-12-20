import discord
from discord.ext import commands
import os 
from settings import DISCORD_API_KEY

# Features
import example_feat
import google_drive_feat

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
    if message.author.name != bot.user.name and message.content[0] != "!":
        #Uncomment next line to test on_message
        pass
        # await example_feat.send_mess(message)

@bot.event
async def on_command_error(context, exception):
    """
    Coroutine event. Invoked when error has occurred with processing a command. 
    """
    await context.send("An error has occurred with your request. {0}".format(exception))


# ================================================================================
# Commands

@bot.command(name="say")
async def say(ctx, arg):
    """
    Test bot command. Type !say "Message here"
    """

    await ctx.send(arg)

@bot.command(name="users")
async def users(ctx):
    """
    Bot command get list of users. Type !users
    """

    usernames = map(lambda user : user.name, bot.users)
    usernames = list(usernames)

    await ctx.send(usernames)

@bot.command(name="files")
async def files(ctx):
    files = google_drive_feature.get_recent_files()

    # print(files)

    output = "\n"
    for file in files:
        output += (file["name"] + "\n")

    await ctx.send(output)

def main():
    """
    The entry point for the bot. Called in __main__.py
    """
    bot.run(DISCORD_API_KEY)
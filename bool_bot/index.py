import discord
from discord.ext import commands
import os 
from settings import DISCORD_API_KEY
import io

# Features
import example_feat
import google_drive_feat

# Use bot commands extension. 
# Tutorial: https://discordpy.readthedocs.io/en/latest/ext/commands/index.html
# API: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#bot

# File Documentation: https://discordpy.readthedocs.io/en/latest/api.html#file
# Embed Documentation: https://discordpy.readthedocs.io/en/latest/api.html#discord.Embed
# Context Documentation: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context

# ================================================================================
# Temp directory
temp_dir = "./bool_bot/files/"

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
    """
    Command for returning the recent files on google drive. 
    """
    files = google_drive_feat.get_recent_files()

    # print(files)

    output = "\n"
    for file in files:
        print(file)
        output += (file["name"] + "\n")

    await ctx.send(output)

@bot.command(name="phototest")
async def phototest(ctx):
    """
    Testing if local photo can be uploaded to discord. Type !phototest
    """
    file_buffered_io_stream = open("./bool_bot/files/red.jpeg", "rb")
    file_photo = discord.File(file_buffered_io_stream, filename="red.jpeg")

    embed = discord.Embed(title="The Gang", description="Wow an uploaded image")
    embed.set_image(url="attachment://red.jpeg")

    await ctx.send("Sending Photo", file=file_photo, embed=embed)

@bot.command(name="photo_id")
async def photo_id(ctx, file_id):
    """
    Send a photo by photo id. Type !photo_id "google_file_id"

    Ex. !photo 1vACqpQLkve6mLC1tIAEmlrZoUiiaoiaU
    """
    await send_photo(ctx, file_id, "Cooltitle", "Wow downloaded from google drive")

@bot.command(name="photo")
async def photo(ctx, photo_name):
    """
    Send a photo by exact photo name including extension. Type !photo "photo name"

    Ex. !photo jeyalex111.jpg
    """
    obj = google_drive_feat.get_file_id(photo_name)

    if len(obj) == 0:
        await ctx.send("No photo found by that name")
        return

    file_id = obj[0]['id']
    file_name = obj[0]['name']
    web_link = obj[0]["webViewLink"]

    await send_photo(ctx, file_id, file_name, web_link)
    

# ================================================================================
# Helper functions
async def send_photo(ctx, file_id, file_name, description):
    """
    Sends the photo to where the command is issued

    ctx : Context - A contex class. Part of discord.py. Refer to do here (https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#context)
    file_id : String - The google drive file id. 
    file_name : String - The output file name shown in discord.
    """

    photo_name = google_drive_feat.download_photo(file_id, file_name)

    # Reads file from local storage
    buffered = open(temp_dir + photo_name, "rb")
    file_photo = discord.File(buffered, filename=photo_name)

    embed = discord.Embed(title=photo_name, description=description)
    embed.set_image(url="attachment://" + photo_name)

    await ctx.send("Sending Photo", file=file_photo, embed=embed)

    # Deletes file from local storage
    os.remove(temp_dir + photo_name)

    buffered.close()

    return

def main():
    """
    The entry point for the bot. Called in __main__.py
    """
    bot.run(DISCORD_API_KEY)
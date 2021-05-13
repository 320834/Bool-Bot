import discord
from discord.ext import commands
from settings import DISCORD_API_KEY
from settings import ROOT_PHOTO_FOLDER_ID
import asyncio

# Features
import example_feat
import google_drive_feat
import photo
import channel
import video

# Use bot commands extension.
# Tutorial: https://discordpy.readthedocs.io/en/latest/ext/commands/index.html
# API: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#bot

# File Documentation: https://discordpy.readthedocs.io/en/latest/api.html#file
# Embed Documentation: https://discordpy.readthedocs.io/en/latest/api.html#discord.Embed
# Context Documentation: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context

# ================================================================================
# Global vars

# ================================================================================
# Temp directory
temp_dir = "./bool_bot/files/"
search_requests = {}

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
    Coroutine event. Invoked when user sends a message
    """

    # Ensure no feedback loop from bot.
    if message.author.name == bot.user.name:
        #Return nothing so bot does not respond to it's own message
        return

    if len(channel.bot_channels) == 0 and message.content[0] == "!" and message.content.find("!channel") == -1:
        return await message.channel.send("There are no bot channels. Use !channel add channel_name")

    # Process only channel commands
    if (message.content.find("!channel") != -1):
        return await bot.process_commands(message)

    if message.channel.name in channel.bot_channels:
        await bot.process_commands(message)

        await process_search_request(message)
        # await example_feat.send_mess(message)

@bot.event
async def on_command_error(context, exception):
    """
    Coroutine event. Invoked when error has occurred with processing a command.
    """
    await context.send("An error has occurred with your request. {0}".format(exception))


# ================================================================================
# Commands

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

@bot.command(name="photo")
async def photo_command(ctx, search_option, query):
    """
    Photo commands. Refer below for commands.

    Flags

    s or search - Search for a photo via name. Ex. !photo s kurt
    e or exact - Return a photo with exact name. Ex. !photo e davidmald.jpg
    i or id - Return a photo by google drive id. Ex. !photo i 1CeUaHMY5-Fm5XD36u3QWUZLaG6qAZUPq
    r or random - Return a photo randomly from a query. Ex. !photo r justin
    rf or randomfile - Return a photo randomly from a specified folder. Ex. !photo rf test

    """

    if search_option == "s" or search_option == "search":
        # Searches for photos with name
        await photo.photo_search(ctx, query)
    elif search_option == "e" or search_option == "exact":
        # Find and return photo with exact name
        await photo.photo_name(ctx, query)
    elif search_option == "i" or search_option == "id":
        # Find and return photo with google id
        await photo.photo_id(ctx, query)
    elif search_option == "r" or search_option == "random":
        # Return random photo from recent files list
        await photo.photo_random(ctx, query)
    elif search_option == "rf" or search_option == "randomfile":
        # Return random photo from a specified folder
        await photo.folder_random(ctx, query)
    else:
        await ctx.send("Something is wrong with your query, most likely that the option you provided is not valid")

@bot.command(name="video")
async def video_command(ctx, search_option, query):
    """
    Video commands. 

    Flags

    r or random - Searches for a video with query and return a random one. Ex. !video r jey
    """
    if search_option == "r" or search_option == "random":
        await video.video_random(ctx, query)
    elif search_option == "s" or search_option == "search":
        await video.video_search(ctx, query)
    else:
        await ctx.send("Something is wrong with your query, most likely that the option you provided is not valid")


@bot.command(name="listrequests")
async def list_requests(ctx):
    """
    A development command to inspect the photo requests
    Note: This can interfere with time out request deletion
    """
    print(search_requests)

@bot.command(name="ls")
async def ls(ctx):
    """
    Lists the subdirectories in root photo folder. Useful for finding a random photo in a folder
    """
    folder_ids, folder_names = google_drive_feat.get_folder_ids(ROOT_PHOTO_FOLDER_ID)
    description = ''

    for i in range(len(folder_names)-1):
        description += "{0}. {1}\n".format(i, folder_names[i])
        # Send decision embed
    embed = discord.Embed(title='Sub-directories found:')
    embed.description = description

    # Takes discord message type
    message = await ctx.send(embed=embed)
    
@bot.command(name="channel-list")
async def channel_list(ctx):
    """
    Command to list which channels is the bot allowed be issued commands
    """
    channels = ctx.guild.text_channels
    
    bot_active_channels = []
    bot_nonactive_channels = []

    for curr_channel in channels:
        if curr_channel.name in channel.bot_channels:
            bot_active_channels.append(curr_channel.name)
        else:
            bot_nonactive_channels.append(curr_channel.name)        

    active_bot_message = "\n".join(bot_active_channels)
    nonactive_bot_message = "\n".join(bot_nonactive_channels)

    message = "Bot Access Channels\n\n{0}\n\nBot Non Access Channels\n\n{1}".format(active_bot_message, nonactive_bot_message)
    embed = discord.Embed(title="Bot Permissions channel", description=message)
    return await ctx.send("", embed=embed)

@bot.command(name="channel")
async def channel_command(ctx, flag, query):
    """
    Add or remove bot from a specific channel. If added to a specific channel, regular users can issue bot commands. 
    WARNING: Need to be an admin of the guild to issue this command

    Flags
    a or add - Add a bot to a channel. Ex. !channel a bool-bol-test
    d or delete - Remove a bot from a channel. Ex. !channel d bool-bot-test
    """

    # Make sure user is an admin

    if not ctx.author.guild_permissions.administrator:
        return

    if flag == "a" or flag == "add":
        await channel.channel_add(ctx, query)
    elif flag == "r" or flag == "remove":
        await channel.channel_remove(ctx, query)
    else:
        return await ctx.send("Issues with your request. Are you sure you are entering the right flags")


# Helper functions

async def process_search_request(message):
    """
    Process search request(photo or video) of requesting user
    """
    user_id = message.author.id
    res = message.content

    if not (user_id in search_requests):
        # Found nothing. No request for this user.
        return

    if bool(search_requests) and search_requests[user_id] != None and message.content == 'c':

        message = search_requests[user_id]["message"]
        # Delete query embed
        await message.delete()

        del search_requests[user_id]

        return await message.channel.send("Cancelling Request")

    if bool(search_requests) and search_requests[user_id] != None:

        index = None
        try:
            index = int(res)
        except ValueError:
            return await message.channel.send("Please enter a number")

        try:
            file_id = search_requests[user_id]["files"][index]["id"]
            file_name = search_requests[user_id]["files"][index]["name"]
            description = search_requests[user_id]["files"][index]["webViewLink"]
            request_type = search_requests[user_id]["type"]

            message = search_requests[user_id]["message"]

            # Delete query embed
            await message.delete()

            # Third argument takes file id as the file name. Due to privacy reasons, we won't upload the photo name to discord
            if request_type == 'photo':
                await photo.send_photo(message.channel, file_id, "{0}.jpeg".format(file_id), description)
            elif request_type == 'video':
                await video.send_video(message.channel, file_id, "{0}.mp4".format(file_id))
            else:
                await message.channel.send("Error: invalid request type")
        except IndexError:
            return await message.channel.send("Please enter a number in range of request")

        # Remove user key from photo requests
        del search_requests[user_id]

        return

def main():
    """
    The entry point for the bot. Called in __main__.py
    """
    bot.run(DISCORD_API_KEY)

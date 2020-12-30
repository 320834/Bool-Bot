import discord
from discord.ext import commands
import os 
from settings import DISCORD_API_KEY
import io
import random

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
# Global vars

photo_requests = {}

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
    Coroutine event. Invoked when user sends a message
    """
    result = await bot.process_commands(message)

    # Ensure no feedback loop.
    if message.author.name != bot.user.name and message.content[0] != "!":
        #Uncomment next line to test on_message
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
async def photo(ctx, search_option, query):
    if search_option == "s" or search_option == "search":
        # Searches for photos with name
        await photo_search(ctx, query)
        pass
    elif search_option == "e" or search_option == "exact":
        # Find and return photo with exact name
        await photo_name(ctx, query)
        pass
    elif search_option == "i" or search_option == "id":
        # Find and return photo with google id
        await photo_id(ctx, query)
        pass
    elif search_option == "r" or search_option == "random":
        # Return random photo from recent files list
        await photo_random(ctx, query)
        pass
    
@bot.command(name="listrequests")
async def list_requests(ctx):
    print(photo_requests)

# ================================================================================
# Helper functions

async def photo_random(ctx, query):
    
    #files = google_drive_feat.get_recent_files()
    #random_file_id = files[0]["id"]

    found_files = google_drive_feat.get_files_search(query)
    random_file_id = found_files[random.randint(0, len(found_files))]["id"]

    await send_photo(ctx, random_file_id, "{0}.jpeg".format(random_file_id), "random file")

async def photo_id(ctx, file_id):
    """
    Send a photo by photo id. Type !photo_id "google_file_id"

    Ex. !photo 1vACqpQLkve6mLC1tIAEmlrZoUiiaoiaU
    """
    await send_photo(ctx, file_id, "{0}.jpeg".format(file_id), "Wow downloaded from google drive")

async def photo_name(ctx, photo_name):
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

    await send_photo(ctx, file_id, file_id, web_link)

async def photo_search(ctx, query):

    #Check if current user has a pending request
    if (ctx.author.id in photo_requests):
        # Found pending request. Deny 
        return ctx.send("Pending request, please chose or enter c to cancel")

    # Continue with query
    found_files = google_drive_feat.get_files_search(query)

    description = ""

    for i in range(0 , len(found_files)):
        file = found_files[i]

        description += "{0}. {1}\n".format(i, file['name'])

    # Send decision embed
    embed = discord.Embed(title="Select an option. Enter a number from list. Enter c to cancel")
    embed.description = description

    await ctx.send(embed=embed)
    
    # Push request to photo requests
    photo_requests[ctx.author.id] = found_files

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

    buffered.close()

    # Deletes file from local storage
    os.remove(temp_dir + photo_name)


    return

async def process_search_request(message):
    """
    Process search request of requesting user
    """
    user_id = message.author.id
    res = message.content


    if not (user_id in photo_requests):
        # Found nothing. No request for this user.
        return

    if bool(photo_requests) and photo_requests[user_id] != None and message.content == 'c':
        del photo_requests[user_id]

        return await message.channel.send("Cancelling Request")

    if bool(photo_requests) and photo_requests[user_id] != None:

        index = None
        try:
            index = int(res)
        except ValueError:
            return await message.channel.send("Please enter a number")

        try:
            file_id = photo_requests[user_id][index]["id"]
            file_name = photo_requests[user_id][index]["name"]
            description = photo_requests[user_id][index]["webViewLink"]
            
            # Third argument takes file id as the file name. Due to privacy reasons, we won't upload the photo name to discord
            await send_photo(message.channel, file_id, "{0}.jpeg".format(file_id), description)
        except IndexError:
            return await message.channel.send("Please enter a number in range of request")

        # Remove user key from photo requests
        del photo_requests[user_id]

        return

def main():
    """
    The entry point for the bot. Called in __main__.py
    """
    bot.run(DISCORD_API_KEY)
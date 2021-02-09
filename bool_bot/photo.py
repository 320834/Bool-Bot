import discord
import random
import os
import random
import asyncio

# Features
import google_drive_feat
import index

# Global vars
photo_requests = {}

# ================================================================================
# Photo functions

async def folder_random(ctx, query):
    """
    Send a photo randomly by querying a folder. Type !photo rf test
    """

    files = google_drive_feat.get_folder_contents(query)


    if files == "No Folder":
        return await ctx.send("Folder {0} cannot be found".format(query))
    elif files == "Multiple Folders":
        return await ctx.send("Multiple folders with name {0}. Stopping request".format(query))
    elif len(files) == 0:
        return await ctx.send("No files in folder {0}". format(query))

    random_index = random.randint(0, len(files) - 1)
    random_file_id = files[random_index]["id"]

    await send_photo(ctx, random_file_id, "{0}.jpeg".format(random_file_id), "Random photo from {0}".format(query))


async def photo_random(ctx, query):
    """
    Send random photo based on name in query.

    Ex. !photo r justin
    This command will return a random photo, where the file name contains "justin" or the description contains "justin"

    """
    found_files = google_drive_feat.get_files_search(query)

    if len(found_files) == 0:
        await ctx.send("No random photo found, probably because there are no photo/file names with the query you requested")
        return

    
    random_index = random.randint(0, len(found_files) - 1)
    random_file_id = found_files[random_index]["id"]
    random_file_description = "when the imposter is sus af"

    if "description" in found_files[random_index]:
        random_file_description = found_files[random_index]['description']

    await send_photo(ctx, random_file_id, "{0}.jpeg".format(random_file_id), random_file_description)



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
    """
    Helper function for command photo s query. Process request of a query. Returns an embed with options.
    """

    #Check if current user has a pending request
    if (ctx.author.id in photo_requests):
        # Found pending request. Deny
        return await ctx.send("Pending request, please chose or enter c to cancel")

    # Continue with query
    found_files = google_drive_feat.get_files_search(query)

    if len(found_files) == 0:
        await ctx.send("There are no photos that start with {}".format(query)) # await neeeded???
        return

    description = ""

    for i in range(0 , len(found_files)):
        file = found_files[i]

        description += "{0}. {1}\n".format(i, file['name'])

    # Send decision embed
    embed = discord.Embed(title="Select an option. Enter a number from list. Enter c to cancel")
    embed.description = description

    # Takes discord message type
    message = await ctx.send(embed=embed)

    # Store found_files and message in a dictionary.
    request = {
        "files": found_files,
        "message": message
    }


    # Push request to photo requests
    photo_requests[ctx.author.id] = request
    try:
        await index.bot.wait_for('message',timeout=10.0)
    except asyncio.TimeoutError:
        del photo_requests[ctx.author.id]
        await message.delete()
        await ctx.send('Request {} timed out'.format(query))

async def send_photo(ctx, file_id, file_name, description):
    """
    Sends the photo to where the command is issued

    ctx : Context - A contex class. Part of discord.py. Refer to do here (https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#context)
    file_id : String - The google drive file id.
    file_name : String - The output file name shown in discord.
    description : String - The description of the photo in discord embed
    """

    photo_name = google_drive_feat.download_file(file_id, file_name)

    # Reads file from local storage
    buffered = open(google_drive_feat.temp_dir + photo_name, "rb")
    file_photo = discord.File(buffered, filename=photo_name)

    embed = discord.Embed(title=photo_name, description=description)
    embed.set_image(url="attachment://" + photo_name)

    await ctx.send("Sending Photo", file=file_photo, embed=embed)

    buffered.close()

    # Deletes file from local storage
    os.remove(google_drive_feat.temp_dir + photo_name)
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

        message = photo_requests[user_id]["message"]
        # Delete query embed
        await message.delete()

        del photo_requests[user_id]

        return await message.channel.send("Cancelling Request")

    if bool(photo_requests) and photo_requests[user_id] != None:

        index = None
        try:
            index = int(res)
        except ValueError:
            return await message.channel.send("Please enter a number")

        try:
            file_id = photo_requests[user_id]["files"][index]["id"]
            file_name = photo_requests[user_id]["files"][index]["name"]
            description = photo_requests[user_id]["files"][index]["webViewLink"]

            message = photo_requests[user_id]["message"]

            # Delete query embed
            await message.delete()

            # Third argument takes file id as the file name. Due to privacy reasons, we won't upload the photo name to discord
            await send_photo(message.channel, file_id, "{0}.jpeg".format(file_id), description)
        except IndexError:
            return await message.channel.send("Please enter a number in range of request")

        # Remove user key from photo requests
        del photo_requests[user_id]

        return

async def print_photo_requests():
    print(photo_requests)
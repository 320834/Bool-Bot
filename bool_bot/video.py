import discord
import random
import os
import asyncio

# Features
import google_drive_feat
import index

# ================================================================================
# Video functions
async def video_random(ctx, query):
    """
    Gets a random video based off of query. Searches for video name and in its description

    query : String - The video name or description.  
    """
    found_files = google_drive_feat.get_files_search(query, video=True)
    
    if len(found_files) == 0:
        await ctx.send("No random video found, probably because there are no video names with the query you requested")
        return

    
    random_index = random.randint(0, len(found_files) - 1)
    random_file_id = found_files[random_index]["id"]
    random_file_name = "{}.mp4".format(random_file_id)
    
    await send_video(ctx, random_file_id, random_file_name)

async def video_search(ctx, query):
    """
    Helper function for command photo s query. Process request of a query. Returns an embed with options.
    """

    #Check if current user has a pending request
    if (ctx.author.id in index.search_requests):
        # Found pending request. Deny
        return await ctx.send("Pending request, please chose or enter c to cancel")

    # Continue with query
    found_files = google_drive_feat.get_files_search(query, True)

    if len(found_files) == 0:
        await ctx.send("There are no videos that start with {}".format(query)) # await neeeded???
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
        "message": message,
        "type": 'video'
    }


    # Push request to photo requests
    index.search_requests[ctx.author.id] = request
    try:
        await index.bot.wait_for('message',timeout=10.0)
    except asyncio.TimeoutError:
        del index.search_requests[ctx.author.id]
        await message.delete()
        await ctx.send('Video request {} timed out'.format(query))

async def send_video(ctx, file_id, file_name):
    """
    Works exactly the same way as send_photo, but without the embed since you can't embed videos with discord.py(I may be wrong)
    """

    video_name = google_drive_feat.download_file(file_id, file_name)

    # Reads file from local storage
    buffered = open(google_drive_feat.temp_dir + video_name, "rb")
    file_video = discord.File(buffered, filename=video_name)
    # insert embed code here, if possible

    await ctx.send("Sending Video from Google Drive", file=file_video)

    buffered.close()

    # Deletes file from local storage
    os.remove(google_drive_feat.temp_dir + video_name)

    return
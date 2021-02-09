import discord
import random
import os
import asyncio

# Features
import google_drive_feat


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
    random_file_name = found_files[random_index]["name"]
    
    await send_video(ctx, random_file_id, random_file_name)

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
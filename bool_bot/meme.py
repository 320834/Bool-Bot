import discord
import asyncio
from moviepy.editor import *
import numpy as np
import math

import google_drive_feat
import video
import index

# ====================================================
# Video meme generator

async def generate_meme_video(ctx, text, file_id, file_name):
    video_name = google_drive_feat.download_file(file_id, file_name)

    video_bytes = os.stat(google_drive_feat.temp_dir + video_name).st_size

    if video_bytes > 8000000:
        os.remove(google_drive_feat.temp_dir + video_name)
        return await ctx.send("Size of original video exceed 8 MB. Discord cannot ")


    video = VideoFileClip(google_drive_feat.temp_dir + video_name).set_position("bottom")
    video_width = video.size[0]
    video_height = video.size[1]
    time = video.duration

    FONT_OFFSET = 0.08 # Determines fontsize based on width of video
    fontsize = video_width * FONT_OFFSET
    line_height = int(fontsize)

    # Create text clip
    num_of_lines = determine_lines(text, video_width, fontsize)
    text_clip_array = create_text_clip(num_of_lines, fontsize, time, line_height)

    # Create text white background
    background = create_white_background_clip(video_height, video_width, line_height, num_of_lines, time)

    mes = await ctx.send("Processing Video. Depends on size of original video.")

    # Merge white background and text clip
    result = CompositeVideoClip([background, video] + text_clip_array)
    result.write_videofile(google_drive_feat.temp_dir + "temp.mp4", threads=4, fps=20, logger=None)

    await send_local_video(ctx, video_name)
    await mes.delete()

# ====================================================
# Helper Functions

async def send_local_video(ctx, video_name):
    # Reads file from local storage
    buffered = open(google_drive_feat.temp_dir + "temp.mp4", "rb")
    file_video = discord.File(buffered, filename=video_name)
    
    await ctx.send("Sending Meme Video", file=file_video)

    buffered.close()

    # Deletes file from local storage
    os.remove(google_drive_feat.temp_dir + video_name)
    os.remove(google_drive_feat.temp_dir + "temp.mp4")

    return

def determine_lines(text, width, fontsize):
    """
    When appending text to video. The video does not wrap text if the text is too long
    We have to determine how many lines it takes to include the entire message
    """

    last_line_index = 0
    char_limit = math.floor(width/fontsize) * 2 # Approximate number of characters per line
    buffer= 5

    lines = []

    for i in range(len(text)):

        if(
            text[i] == ' ' and 
            i>=char_limit-buffer and 
            i-last_line_index > 2*buffer and
            (
                i%char_limit >= char_limit - buffer or 
                i%char_limit <= buffer )
            ):

            lines.append(text[last_line_index: i+1])

            last_line_index = i+1

        if(i == len(text) - 1):
            lines.append(text[last_line_index: i+1])

    return lines

def create_text_clip(lines, fontsize, time, line_height):
    """
    Create the text clip that appends to the video 
    """
    text_clip_arr = []

    line_num = 0
    for line in lines:

        text_clip_arr.append(( TextClip(line, font="Impact", stroke_width=2.0, fontsize=fontsize, color= "black")
            .set_position((20, line_height * line_num))
            .set_duration(time)
            ))

        line_num += 1

    return text_clip_arr

def create_white_background_clip(video_height, video_width, line_height, num_of_lines, time):
    text_height = video_height + 20 + line_height*len(num_of_lines)
    array = np.empty((text_height, video_width, 3))
    array.fill(255)
    return ImageClip(array).set_duration(time)
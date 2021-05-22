import discord
import asyncio
from moviepy.editor import *
import numpy as np
import math

import google_drive_feat
import video
import index

FONTSIZE = 70

# ====================================================
# Video meme generator

async def generate_meme_video(ctx, text, file_id, file_name):
    video_name = google_drive_feat.download_file(file_id, file_name)

    fontsize = FONTSIZE

    video = VideoFileClip(google_drive_feat.temp_dir + video_name).set_position("bottom")
    video_width = video.size[0]
    video_height = video.size[1]
    time = video.duration

    lines = determine_lines(text, video_width)
    text_clip_array = create_text_clip(lines, fontsize, time)

    array = np.empty((video_height + 100 * len(lines), video_width, 3))
    array.fill(255)
    background = ImageClip(array).set_duration(video.duration)

    mes = await ctx.send("Processing Video. Depends on size of original video.")

    result = CompositeVideoClip([background, video] + text_clip_array)
    result.write_videofile(google_drive_feat.temp_dir + "temp.mp4", fps=20, logger=None)

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

def determine_lines(text, width):

    last_line_index = 0
    char_limit = math.floor(width/30)
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

def create_text_clip(lines, fontsize, time):

    text_clip_arr = []

    line_num = 0
    for line in lines:

        text_clip_arr.append(( TextClip(line, font="Impact", stroke_width=5.0, fontsize=fontsize, color= "black")
            .set_position((20, 10 + 100*line_num))
            .set_duration(time)
            ))

        line_num += 1

    return text_clip_arr
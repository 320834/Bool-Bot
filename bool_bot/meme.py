import discord
from moviepy.editor import *
import numpy as np
import math

import google_drive_feat

# ====================================================
# Video meme generator

async def generate_meme_video(ctx, text, file_id, file_name):
    video_name = google_drive_feat.download_file(file_id, file_name)

    video_bytes = os.stat(google_drive_feat.temp_dir + video_name).st_size

    if video_bytes > 8000000: # Over 8 MB
        os.remove(google_drive_feat.temp_dir + video_name)
        return await ctx.send("Size of original video exceed 8 MB. Discord cannot send it over 8 MB")


    video = VideoFileClip(google_drive_feat.temp_dir + video_name).set_position("bottom")
    video_width = video.size[0]
    video_height = video.size[1]
    time = video.duration

    FONT_OFFSET = 0.08 # Determines fontsize based on width of video
    fontsize = video_width * FONT_OFFSET
    line_height = int(fontsize)

    # Create text clip
    lines = determine_lines(text, video_width, fontsize)
    text_clip_array = create_text_clip(lines, fontsize, time, line_height)

    # Create text white background
    background = create_white_background_clip(video_height, video_width, line_height, lines, time)

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
    We have to determine how many lines it takes to include the entire message.
    This function returns the lines of the array to be turned into a VideoClip
    """

    last_line_index = 0
    char_limit = math.floor(width/fontsize) * 2 # Approximate number of characters per line
    # The threshold of the char_limit. 
    # char_limit is not perfect. Some characters will be longer in width than others. 
    # So we have this buffer to account for it
    # char_limit - buffer < character_limit < buffer
    BUFFER= 4


    lines = []

    """
    Enumerate through each character and determine if character is part of current line
    or the next line. If character is part of the newline, we save the substring of the characters
    before the newline.
    """
    for index, char in enumerate(text):

        if(
            char == ' ' and # Ensure the dividing char is not a character but a space
            index >= char_limit-BUFFER and # Ensure characters in the beginning are in the first line 
            index-last_line_index > 2*BUFFER and # Ensure current line is atleast 2 twice the length of the buffer
            (
                index%char_limit >= char_limit - BUFFER or # Ensure character index falls between char_limit and the char_limit - buffer
                index%char_limit <= BUFFER) # These are the two core conditional.
            ):

            lines.append(text[last_line_index: index+1])

            last_line_index = index+1


    lines.append(text[last_line_index:])

    return lines

def create_text_clip(lines, fontsize, time, line_height):
    """
    Create the text clip that appends to the video 
    """
    text_clip_arr = []
    Y_OFFSET = 20

    for line_num, line in enumerate(lines):

        text_clip_arr.append(( TextClip(line, font="Impact", stroke_width=2.0, fontsize=fontsize, color= "black")
            .set_position((Y_OFFSET, line_height * line_num))
            .set_duration(time)
            ))


    return text_clip_arr

def create_white_background_clip(video_height, video_width, line_height, num_of_lines, time):
    
    Y_OFFSET = 20
    
    text_height = video_height + Y_OFFSET + line_height*len(num_of_lines)
    array = np.empty((text_height, video_width, 3))
    array.fill(255)
    return ImageClip(array).set_duration(time)
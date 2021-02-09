import discord
import asyncio

# Global Vars
bot_channels = {}

# ================================================================================
# Channel functions

async def channel_add(ctx, name):
    """
    Add a bot to a channel via name
    """

    if name in bot_channels:
        return await ctx.send("Channel already added")

    channels = ctx.guild.text_channels

    found_channels = filter(lambda channel: channel.name == name, channels)

    if len(list(found_channels)) > 0:
        bot_channels[name] = "no"
        return await ctx.send("Sucessfully added to {0} text channel".format(name))

    return await ctx.send("Cannot find channel {0}".format(name))

async def channel_remove(ctx, name):
    """
    Delete a bot from a channel via name
    """
    
    channels = ctx.guild.text_channels
    found_channels = filter(lambda channel: channel.name == name, channels)

    if not (name in bot_channels) and len(list(found_channels)) > 0:
        return await ctx.send("Cannot delete channel. Channel is not in this channel already")

    if len(list(found_channels)) > 0:
        del bot_channels[name]
        return await ctx.send("Sucessfully remove bot from {0} text channel".format(name))

    return await ctx.send("Cannot find channel {0}".format(name))
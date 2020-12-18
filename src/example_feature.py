async def send_mess(message):
    channel = message.channel

    await channel.send(message.content)
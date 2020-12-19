async def send_mess(message):
    channel = message.channel

    await channel.send(message.content)

def stuff(value):
    return 4 + value

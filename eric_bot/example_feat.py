async def send_mess(message):
    """
    A simple feature takes a message and sends it back to the originating channel
    message : Message (refer to discord py documentation)
    """
    channel = message.channel
    await channel.send(message.content)

    return message.content

def add(value):
    return 4 + value
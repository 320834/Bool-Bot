import pytest

from bool_bot import example_feat

# Async Tests. Use for testing code as most of it will be coroutines
@pytest.mark.asyncio
async def test_send_mess(mocker):
    """
    Test for send_mess. Async test and mocks attributes.

    mocker : Object (Refer to pytest-mocker)
    """
    message_content = "This is true America"

    class Channel(object):
        async def send(self, content):
            return content

    class Message(object):

        channel = Channel()
        spy_channel = mocker.spy(channel, 'send')

        content = message_content

    message = Message()


    res = await example_feat.send_mess(message)

    assert res=="This is true America"
    message.spy_channel.assert_called_once_with("This is true America")

# Standard Tests. Use for helper/private functions
def test_add():
    """

    """
    assert example_feat.add(10) == 14
    assert example_feat.add(-5) == -1
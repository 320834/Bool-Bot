import pytest

from bool_bot import meme


def test_determine_lines():
    """
    Test determine lines
    """

    text = "There are six words in this sentence"
    width = 144
    fontsize = 12

    lines = meme.determine_lines(text, width, fontsize)

    assert len(lines) == 2
    assert lines[0] == "There are six words in "
    assert lines[1] == "this sentence"


def test_create_text_clip():
    lines = [
        "There are size words in ",
        "this sentence"
    ]

    fontsize = 12
    time = 10
    line_height = 15

    text_clip_list = meme.create_text_clip(lines, fontsize, time, line_height)

    assert len(text_clip_list) == 2


def test_create_white_background_clip(mocker):
    video_height = 20
    video_width = 20
    line_height = 12
    num_of_lines = 2
    time = 10

    spy = mocker.spy(meme, 'create_white_background_clip')

    meme.create_white_background_clip(
        video_height, video_width, line_height, num_of_lines, time)

    spy.assert_called_once()

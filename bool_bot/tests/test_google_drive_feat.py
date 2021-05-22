import pytest
import os

from bool_bot import google_drive_feat

@pytest.mark.asyncio
async def test_get_recent_files(mocker):
    """
    Test get recent files
    """

    spy = mocker.spy(google_drive_feat, 'get_recent_files')

    items = google_drive_feat.get_recent_files()
    
    spy.assert_called_once()
    assert len(items) == 10

@pytest.mark.asyncio
async def test_get_file_id(mocker):
    """
    Test get file id
    """

    # Test no files
    id_one = google_drive_feat.get_file_id("swimmerkurt.jpg")
    id_two = google_drive_feat.get_file_id("NONE")

    obj = id_one[0]
    
    assert "id" in obj.keys()
    assert "name" in obj.keys()
    assert "webViewLink" in obj.keys()

    assert len(id_one) == 1
    assert len(id_two) == 0

@pytest.mark.asyncio
async def test_download_photo(mocker):
    """
    Test download file
    """

    # Test no files
    spy = mocker.spy(google_drive_feat, 'download_file')

    filename = google_drive_feat.download_file("19ht1cJrUotOvJL58QemRlZNnmOzUn7GV", "kurt.png")

    spy.assert_called_once_with("19ht1cJrUotOvJL58QemRlZNnmOzUn7GV", "kurt.png")
    assert filename == "kurt.png"
    try:
        os.remove("./bool_bot/files/kurt.png")
    except:
        # os.remove("./bool_bot/files/")
        assert False

@pytest.mark.asyncio
async def test_get_files_search(mocker):
    """
    Test get files search
    """

    spy = mocker.spy(google_drive_feat, "get_files_search")

    results = google_drive_feat.get_files_search("jey")

    spy.assert_called_once_with("jey")
    assert len(results) > 0
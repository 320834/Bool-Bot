from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io

from bool_bot.settings import ROOT_PHOTO_FOLDER_ID

# Documentation Links
# In-depth documentation:
# https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html
# Tutorial Documentation:
# https://developers.google.com/drive/api/v3/about-files

# Root File ID For Photo


# Temp Dir
temp_dir = "./bool_bot/files/"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    """
    Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google-drive-credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_recent_files():
    """
    Returns the 10 most recent files

    return items : Array<Object(id, name)> - An array of objects/dicts with id and name attributes
    """
    creds = authenticate()

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    return items

def get_file_id(filename):
    """
    Get file id from the name

    filename : String - The file name

    return found_files : Array<Object(id, name, webViewLink)> - The file id from google drive
    """

    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    page_token = None
    response = service.files().list(q="name = '{0}'".format(filename),
                                    pageSize=1,
                                    spaces="drive",
                                    fields='nextPageToken, files(id, name, webViewLink)',
                                    pageToken=page_token).execute()

    return response["files"]

def download_file(fileId, fileName):
    """
    Download the photo to local directory.

    fileId : String - The file id
    fileName : String - The file name

    return : String - The file name
    """
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    request = service.files().get_media(fileId=fileId)

    # print(request)

    # Downloads the photo to local storage.
    fh = io.FileIO(temp_dir + fileName, mode='wb')
    downloader = MediaIoBaseDownload(fd=fh, request=request)


    done = False
    while done is False:
        status,done = downloader.next_chunk()
        # print("Download %d%%." % int(status.progress() * 100))

    fh.close()

    return fileName

def get_folder_ids(root_folder_id):
    """
    Returns all the sub folder IDs starting at root_folder(includes the root_folder ID). Goes one level deep.

    Ex: If the root folder has folder1, folder2 and folder3 in it, this will return a list of length 4 with the IDs associated
    with those 3 folders, and the ID of the root folder. However if the 3 folders have subfolders in them as well, this function will not return those subfolder IDs.

    Note: If more than one level deep is needed, a recursive version can be implemented. However this might get very slow if the folder tree structure gets very
    complex. Refer to this if needed: https://stackoverflow.com/questions/41741520/how-do-i-search-sub-folders-and-sub-sub-folders-in-google-drive
    """
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    page_token = None
    response = service.files().list(q="mimeType = 'application/vnd.google-apps.folder' and '{}' in parents and trashed = false".format(root_folder_id),
                                    pageSize=10,
                                    spaces="drive",
                                    fields='nextPageToken, files(id, name, webViewLink)',
                                    pageToken=page_token,

                                    ).execute()
    found_ids = [response["files"][i]["id"] for i in range(0, len(response["files"]))] # extract all the IDs
    found_names = [response["files"][i]["name"] for i in range(0, len(response["files"]))]
    found_ids.append(root_folder_id) # if the Photos folder(as named on Google Drive) just contains folders, this is not needed

    return found_ids, found_names

def get_folder_contents(query):
    """
    Get the file contents of a specific folder.

    query : String - The folder query

    return : Array<Object(id, name, webViewLink)> - An array of files. Each file has id, name, and webViewLink attributes
    """
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    #Fetch folder id of query. Should return one folder id. Structure {'files': [{'id': 'aase8f828efe82'}]}
    page_token = None
    response = service.files().list(
        q="parents in '{0}' and name = '{1}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false".format(ROOT_PHOTO_FOLDER_ID, query),
        pageSize=10,
        spaces="drive",
        fields='nextPageToken, files(id)',
        pageToken=page_token,
    ).execute()

    if(len(response["files"]) > 1):
        return "Multiple Folders"

    if(len(response["files"]) == 0):
        return "No Folder"

    folder_id = response["files"][0]["id"]

    #Return the first 100 files in the folder
    page_token = None
    response = service.files().list(
        q="parents in '{0}' and trashed = false and (mimeType = 'image/jpeg' or mimeType = 'image/png' or mimeType = 'image/svg+xml')".format(folder_id),
        pageSize=100,
        spaces="drive",
        fields='nextPageToken, files(id, name, webViewLink)',
        pageToken=page_token,
    ).execute()

    return response["files"]


def get_files_search(query, video=False):
    """
    Get the files that contains the query. Matches it with file name. 

    query : String - The query

    return found_files : Array<Object(id, name, webViewLink)> - The number of found files
    """

    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    folder_ids, folder_names = get_folder_ids(ROOT_PHOTO_FOLDER_ID)
    files = []
    found_files = []
    gd_query = "'{}' in parents and trashed = false and (mimeType = 'image/jpeg' or mimeType = 'image/png' or mimeType = 'image/svg+xml')"

    if video:
        gd_query = "'{}' in parents and trashed = false and mimeType = 'video/mp4'"

    for id in folder_ids:
        page_token = None
        response = service.files().list(q=gd_query.format(id),
                                        pageSize=10,
                                        spaces="drive",
                                        fields='nextPageToken, files(id, name, webViewLink, description)',
                                        pageToken=page_token,

                                        ).execute()
        files.extend(response["files"]) # simply add to the current list of files found in other folders

    for file in files:
        if (
            file["name"].rfind(query) != -1 or 
            "description" in file and file["description"].rfind(query) != -1
        ):
            found_files.append(file)

    return found_files
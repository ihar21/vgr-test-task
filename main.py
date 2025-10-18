import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request 
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

#--SETTINGS--
#>AUTHENTICATION
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive']
#>FOLDERS ID
SOURCE_ROOT_FOLDER_ID = "1R3hDscEc_Ujh1FytqWROg4tS__qcO1Ub"
SOURCE_AUDIO_FOLDER_ID = "1dpKG-eaFg2glOovkI4sYgLyPo3mW9Ilg"
DESTINATION_AUDIO_FOLDER_ID = ""
DESTINATION_ROOT_FOLDER_ID = "1PsjppOUaAbFqf4sjcZE8t1jyNaqJYfXV"
#--SETTINGS END--

#--FUNCTIONS--
def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def create_folder(service, name, parent_id=None):
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]
    folder = service.files().create(body=metadata, fields='id').execute()
    return folder.get('id')

def upload_file(service, file_path, parent_id):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [parent_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def copy_file(service, file_id, new_name, parent_id):
    file_metadata = {
        'name': new_name,
        'parents': [parent_id]
    }
    copied_file = service.files().copy(fileId=file_id, body=file_metadata).execute()
    return copied_file.get('id')

if __name__ == "__main__":
    service = authenticate()
    DESTINATION_AUDIO_FOLDER_ID = create_folder(service, "Records", DESTINATION_ROOT_FOLDER_ID)
    result=list_files_in_folder(service, SOURCE_AUDIO_FOLDER_ID)
    for file in result:
        #print(f"Found file: {file['name']} (ID: {file['id']})")
        copy_file(service, file['id'], file['name'], DESTINATION_AUDIO_FOLDER_ID)
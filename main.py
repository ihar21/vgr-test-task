import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request 
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from google import genai
from google.genai import types
from config import TOKEN_FILE, CREDENTIALS_FILE, SCOPES, SOURCE_AUDIO_FOLDER_ID, DESTINATION_ROOT_FOLDER_ID, GENAI_API_KEY, GENAI_MODEL, MIME_TYPE
from promts import PROMT

destination_audio_folder = None

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

def upload_bytes(service, file_name, file_bytes, parent_id):
    file_metadata = {
        'name': file_name,
        'parents': [parent_id]
    }
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype='application/octet-stream', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def download_audio_bytes(service, file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh.read()

def get_file_name(service, file_id):
    file = service.files().get(fileId=file_id, fields='name').execute()
    return file.get('name')

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

def LLM_transcribe_and_analyze(client, audio_bytes, prompt):
    try:
        response = client.models.generate_content(
            model= GENAI_MODEL,
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=MIME_TYPE,
                ),
            ],
        )
        return response.text
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def main():
    service = authenticate()
    #destination_audio_folder = create_folder(service, "Records", DESTINATION_ROOT_FOLDER_ID)
    result=list_files_in_folder(service, SOURCE_AUDIO_FOLDER_ID)
    #test_text = b"Test upload from bytes"
    #upload_bytes(service, "test_bytes_upload.txt", test_text, DESTINATION_ROOT_FOLDER_ID)
    #for file in result:
        #print(f"Found file: {file['name']} (ID: {file['id']})")
        #copy_file(service, file['id'], file['name'], DESTINATION_AUDIO_FOLDER_ID)
    #copy_file(service, '12RRthiUDo98R2ZCs13YL2ktdzfQnhCT9', '2025-09-10_15-52_0632838007_incoming.mp3', destination_audio_folder)
    result=list_files_in_folder(service, "1St5Zse4pBw34MYjG6wT7-pYlH2a3P2Jw")
    #print(result[0]['id'])
    client = genai.Client(api_key=GENAI_API_KEY)
    audio_bytes = download_audio_bytes(service, result[0]['id'])
    transcription = LLM_transcribe_and_analyze(client, audio_bytes, PROMT)
    upload_bytes(service, "transcription.txt", transcription.encode('utf-8'), "1St5Zse4pBw34MYjG6wT7-pYlH2a3P2Jw")


if __name__ == "__main__":
    main()
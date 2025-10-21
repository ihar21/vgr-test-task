from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request 
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
import os
import io
from config import TOKEN_FILE, CREDENTIALS_FILE, SCOPES

class GoogleDriveManager:
    
    def __init__(self):
        self.creds = self._authenticate()
        self.service_drive = build('drive', 'v3', credentials=self.creds)
        self.service_sheets = build('sheets', 'v4', credentials=self.creds)

    def _authenticate(self):
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
        return creds  
    
    def create_folder(self, name, parent_id=None):
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            metadata['parents'] = [parent_id]
        folder = self.service_drive.files().create(body=metadata, fields='id').execute()
        return folder.get('id')
    
    def upload_file(self, file_path, parent_id):
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [parent_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    
    def upload_bytes(self, file_name, file_bytes, parent_id):
        file_metadata = {
            'name': file_name,
            'parents': [parent_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype='application/octet-stream', resumable=True)
        file = self.service_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    
    def download_audio_bytes(self, file_id):
        request = self.service_drive.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh.read()
    
    def get_file_name(self, file_id):
        file = self.service_drive.files().get(fileId=file_id, fields='name').execute()
        return file.get('name')
    
    def list_files_in_folder(self, folder_id):
        query = f"'{folder_id}' in parents and trashed=false"
        results = self.service_drive.files().list(q=query, fields="files(id, name)").execute()
        return results.get('files', [])
    
    def copy_file(self, file_id, new_name, parent_id):
        file_metadata = {
            'name': new_name,
            'parents': [parent_id]
        }
        copied_file = self.service_drive.files().copy(fileId=file_id, body=file_metadata).execute()
        return copied_file.get('id')
    
    def find_sheet_in_folder(self, folder_id):
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
        results = self.service_drive.files().list(q=query, fields="files(id, name)").execute()
        return results.get('files', [])[0]
    
    def clear_sheet(self, sheet_id, range_name):
        body = {}
        result = self.service_sheets.spreadsheets().values().clear(
            spreadsheetId=sheet_id, range=range_name, body=body).execute()
        
    def sheet_append_values(self, sheet_id, range_name, values):
        body = {
            'values': values
        }
        result = self.service_sheets.spreadsheets().values().append(
            spreadsheetId=sheet_id, range=range_name,
            valueInputOption='RAW', body=body).execute()  

    def sheet_format(self, sheet_id, requests):     
        body = {
            'requests': requests
        }
        response = self.service_sheets.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body=body).execute()
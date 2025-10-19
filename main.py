import os
from google import genai
from google.genai import types
from config import SOURCE_AUDIO_FOLDER_ID, DESTINATION_ROOT_FOLDER_ID, GENAI_API_KEY, GENAI_MODEL, MIME_TYPE
from promts import PROMT
from drive_manager import GoogleDriveManager

def LLM_transcribe_and_analyze(client, audio_bytes, prompt):
    try:
        response = client.models.generate_content(
            model = GENAI_MODEL,
            contents = [
                prompt,
                types.Part.from_bytes(
                    data = audio_bytes,
                    mime_type = MIME_TYPE,
                ),
            ],
        )
        return response.text
    except Exception as e:
        print(f"Error: {e}")

def main():
    manager = GoogleDriveManager()
    client_gen_ai = genai.Client(api_key=GENAI_API_KEY)
    destination_audio_folder = manager.create_folder("records", DESTINATION_ROOT_FOLDER_ID)
    list_audio_files = manager.list_files_in_folder(SOURCE_AUDIO_FOLDER_ID)
    for i in range(2):
        file = list_audio_files[i]
        print(f"Found file: {file['name']} (ID: {file['id']})")
        manager.copy_file(file['id'], file['name'], destination_audio_folder)
        audio_bytes = manager.download_audio_bytes(file['id'])
        transcription = LLM_transcribe_and_analyze(client_gen_ai, audio_bytes, PROMT)
        new_name = os.path.splitext(file['name'])[0] + "_transcription.txt"
        manager.upload_bytes(new_name, transcription.encode('utf-8'), destination_audio_folder)

if __name__ == "__main__":
    main()
import os
import json
from google import genai
from google.genai import types
from config import SOURCE_AUDIO_FOLDER_ID, SOURCE_ROOT_FOLDER_ID, DESTINATION_ROOT_FOLDER_ID, GENAI_API_KEY\
, GENAI_MODEL, MIME_TYPE, SHEET_NAME, HIDE_CONVERSATION_WITHOUT_NAME, DESTINATIO_AUDIO_FOLDER_NAME
from promts import build_promt
from drive_manager import GoogleDriveManager
import re
from sheet_format_re import form_requests, make_copy_request
import time

def LLM_transcribe_and_analyze(client: genai.Client, audio_bytes: bytes, prompt: str, retrys = 2) -> dict:
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
        text = re.sub(r"^```[a-zA-Z]*|```$", "", response.text.strip(), flags=re.MULTILINE).strip()
        jdict=json.loads(text, strict=False)
        return jdict
    except Exception as e:
        print(f"Error: {e}")
        if retrys > 0:
            print(f"Retrying in 60s... {retrys} attempts left.")
            time.sleep(60)
            return LLM_transcribe_and_analyze(client, audio_bytes, prompt, retrys - 1)
        
def sheet_add_record(manager: GoogleDriveManager, sheet_id: str, row_values: list, cursor: int):
    manager.sheet_format(sheet_id, make_copy_request(3, cursor))
    manager.sheet_format(sheet_id, make_copy_request(3, cursor, paste_type="PASTE_FORMAT"))
    manager.sheet_append_values(sheet_id, f"A{cursor}", [row_values])

def main():
    #Initialize Google Drive Manager and GenAI Client
    manager = GoogleDriveManager()
    client_gen_ai = genai.Client(api_key=GENAI_API_KEY)
    #Drive preparation
    destination_audio_folder = manager.create_folder(DESTINATIO_AUDIO_FOLDER_NAME, DESTINATION_ROOT_FOLDER_ID)
    list_audio_files = manager.list_files_in_folder(SOURCE_AUDIO_FOLDER_ID)
    #Sheet preparation
    source_sheet = manager.find_sheet_in_folder(SOURCE_ROOT_FOLDER_ID)
    sheet = manager.copy_file(source_sheet['id'], SHEET_NAME, DESTINATION_ROOT_FOLDER_ID)
    manager.clear_sheet(sheet, "A3:T1000")
    manager.sheet_format(sheet, form_requests)
    cursor = 3
    #Work begins here
    for i in range(len(list_audio_files)):
        file = list_audio_files[i]
        #Download audio file
        print(f"Found file: {file['name']} (ID: {file['id']}) Processing...")
        manager.copy_file(file['id'], file['name'], destination_audio_folder)
        audio_bytes = manager.download_audio_bytes(file['id'])
        #Get LLM answer
        answer = LLM_transcribe_and_analyze(client_gen_ai, audio_bytes, build_promt(file['name']))
        transcription = answer.get("transcript_section").get("transcription")
        questions = answer.get("analysis_section").get("questions")
        answers = [int(q['answer']) if (q['answer'] in ('1', '0') and i > 10) else q['answer'] for i, q in enumerate(questions)]
        answers[0] = transcription
        #Write to sheet
        if HIDE_CONVERSATION_WITHOUT_NAME:
            if answers[4] != "":
                sheet_add_record(manager, sheet, answers, cursor)
                cursor += 1
        else:
            sheet_add_record(manager, sheet, answers, cursor)
            cursor += 1
        #Upload transcription as txt file
        new_name = os.path.splitext(file['name'])[0] + "_transcription.txt"
        manager.upload_bytes(new_name, transcription.encode('utf-8'), destination_audio_folder)
    

if __name__ == "__main__":
    main()
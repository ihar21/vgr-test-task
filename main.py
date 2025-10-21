import os
import json
from google import genai
from google.genai import types
from config import SOURCE_AUDIO_FOLDER_ID, SOURCE_ROOT_FOLDER_ID, DESTINATION_ROOT_FOLDER_ID, GENAI_API_KEY, GENAI_MODEL, MIME_TYPE
from promts import build_promt
from drive_manager import GoogleDriveManager
import re
from sheet_format_re import form_requests, make_copy_request

def LLM_transcribe_and_analyze(client, audio_bytes, prompt) -> dict:
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

def main():
    manager = GoogleDriveManager()
    client_gen_ai = genai.Client(api_key=GENAI_API_KEY)
    destination_audio_folder = manager.create_folder("records", DESTINATION_ROOT_FOLDER_ID)
    list_audio_files = manager.list_files_in_folder(SOURCE_AUDIO_FOLDER_ID)
    source_sheet = manager.find_sheet_in_folder(SOURCE_ROOT_FOLDER_ID)
    sheet = manager.copy_file(source_sheet['id'], source_sheet['name'], DESTINATION_ROOT_FOLDER_ID)
    manager.clear_sheet(sheet, "A3:T100")
    manager.sheet_format(sheet, form_requests)
    cursor = 3
    for i in range(len(list_audio_files)):
        file = list_audio_files[i]
        print(f"Found file: {file['name']} (ID: {file['id']}) Processing...")
        manager.copy_file(file['id'], file['name'], destination_audio_folder)
        audio_bytes = manager.download_audio_bytes(file['id'])
        answer = LLM_transcribe_and_analyze(client_gen_ai, audio_bytes, build_promt(file['name']))
        transcription = answer.get("transcript_section").get("transcription")
        questions = answer.get("analysis_section").get("questions")
        answers = [int(q['answer']) if (q['answer'] in ('1', '0') and i > 10) else q['answer'] for i, q in enumerate(questions)]
        #print(answers)
        answers[0] = transcription
        if cursor !=3: manager.sheet_format(sheet, make_copy_request(3, cursor))
        if cursor !=3: manager.sheet_format(sheet, make_copy_request(3, cursor, paste_type="PASTE_FORMAT"))
        manager.sheet_append_values(sheet, f"A{cursor}", [answers])
        cursor += 1
        new_name = os.path.splitext(file['name'])[0] + "_transcription.txt"
        manager.upload_bytes(new_name, transcription.encode('utf-8'), destination_audio_folder)
    

if __name__ == "__main__":
    main()
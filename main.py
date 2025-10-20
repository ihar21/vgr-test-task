import os
from google import genai
from google.genai import types
from config import SOURCE_AUDIO_FOLDER_ID, DESTINATION_ROOT_FOLDER_ID, GENAI_API_KEY, GENAI_MODEL, MIME_TYPE
from promts import PROMT
from drive_manager import GoogleDriveManager
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

MAX_LLM_REQUESTS_PER_MIN = 10
lock = threading.Lock()
llm_timestamps = []

def rate_limit_llm():
    global llm_timestamps
    with lock:
        now = time.time()
        # убираем старые запросы
        llm_timestamps = [t for t in llm_timestamps if now - t < 60]
        if len(llm_timestamps) >= MAX_LLM_REQUESTS_PER_MIN:
            sleep_time = 60 - (now - llm_timestamps[0])
            print(f"Wait {sleep_time:.1f} sec — LLM limit reached")
            time.sleep(sleep_time)
        llm_timestamps.append(time.time())

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

def file_worker(manager, client_gen_ai, file, destination_audio_folder):
    time.sleep(0.2) 
    print(f"Found file: {file['name']} (ID: {file['id']}) Processing...")
    manager.copy_file(file['id'], file['name'], destination_audio_folder)
    #audio_bytes = manager.download_audio_bytes(file['id'])
    #transcription = LLM_transcribe_and_analyze(client_gen_ai, audio_bytes, PROMT)
    #new_name = os.path.splitext(file['name'])[0] + "_transcription.txt"
    #manager.upload_bytes(new_name, transcription.encode('utf-8'), destination_audio_folder)

def main():
    #threa
    manager = GoogleDriveManager()
    client_gen_ai = genai.Client(api_key=GENAI_API_KEY)
    destination_audio_folder = manager.create_folder("recordsv1thread", DESTINATION_ROOT_FOLDER_ID)
    list_audio_files = manager.list_files_in_folder(SOURCE_AUDIO_FOLDER_ID)
    #for i in range(2):
        #file = list_audio_files[i]
        #print(f"Found file: {file['name']} (ID: {file['id']}) Processing...")
        #manager.copy_file(file['id'], file['name'], destination_audio_folder)
        #audio_bytes = manager.download_audio_bytes(file['id'])
        #transcription = LLM_transcribe_and_analyze(client_gen_ai, audio_bytes, PROMT)
        #new_name = os.path.splitext(file['name'])[0] + "_transcription.txt"
        #manager.upload_bytes(new_name, transcription.encode('utf-8'), destination_audio_folder)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(file_worker, manager, client_gen_ai, fid, destination_audio_folder) for fid in list_audio_files]
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    main()
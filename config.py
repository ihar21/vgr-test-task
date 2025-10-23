#AUTHENTICATION
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/drive'
    ,'https://www.googleapis.com/auth/spreadsheets']
#FOLDERS ID
SOURCE_ROOT_FOLDER_ID = "1R3hDscEc_Ujh1FytqWROg4tS__qcO1Ub"
SOURCE_AUDIO_FOLDER_ID = "1dpKG-eaFg2glOovkI4sYgLyPo3mW9Ilg"
DESTINATION_ROOT_FOLDER_ID = "YOUR_DESTINATION_GOOGLE_ROOT_FOLDER_ID_HERE"
#GEmini API
GENAI_API_KEY = "YOUR_API_KEY_HERE"
GENAI_MODEL = "gemini-2.5-flash"
MIME_TYPE = "audio/mp3"
#DRIVE
DESTINATIO_AUDIO_FOLDER_NAME = "Records(Final)"
#SHEET
SHEET_NAME = "Звіт проослухованних розмов(Final)"
HIDE_CONVERSATION_WITHOUT_NAME = False # Не вписувати записи де менеджер не називає свого ім'я. True - не вписувати, False - вписувати всі записи.

# Тестове завдання. Інструкція до запуску
---
## 1)Налаштування Google Cloude
1. Зайти і авторізоватися на [Google Cloude](https://console.cloud.google.com/)
2. На горі ***Select a Project***
3. ***New project***
4. Вписати назву і натиснути ***Create***. Обрати через ***Select a Project***
5. ***APIs & Services > Enable APIs & Services***
6. Нагорі ***+ Enable APIs & Services***
7. В пошуку знайти ***Google Drive API*** Потім ***Enable***
8. Повторити для ***Google Sheets API***
9. Далі ***APIs & Services > OAuth consent screen*** і там буде синя кнопка ***Get started***
10. Заповнити. В ***Audience*** обрати ***External***. Натиснути ***Create***
11. Потім в ***Audience*** натиснути ***Add user*** і дотати пошту якою будете авторізуватися для OAuth
12. Далі ***Clients*** > ***Create client***. ***Application type*** поставити ***Desktop app***.
13. ***Create***. **!Важливо** В відкрившимся окні нажати внизу ***Download JSON*** завнтажити цей файл можно один раз на одном клієнті
14. Переіменувати файл в *credentials.json* і покласти біля *main.py*
## 2)Налаштування GenAI
1. Зайти і авторізоватися на [Google AI Studio](https://aistudio.google.com/)
2. Далі ***Dashboard>API keys***. Вгорі ***Create API key***. Там де ***Choose an imported project*** імпортувати свій проєкт з ***Google Cloude***. ***Create key***
3. Можна скопіювати якщо клацнути на ключ і скопіювати ***API Key*** і ввести *config.py*. Константа **GENAI_API_KEY**
## 3)Запуск кода
1. Відкрити термінал в папці з *main.py*
2. **Опціонально** зробити ***віртуальне середовище***
```shell
python -m venv venv
```
Активація venv 
```shell
venv/Scripts/activate
```
Може знадобиться для активації venv
```shell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
3. Встановити ***залежністі***
```shell
pip install -r requirements.txt
```
4. Налаштувати ***config.py***
>Id гугл папки можно знайти в адрессі сайта гугл діска
```python
#AUTHENTICATION
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json" #Файл з Google Cloude
SCOPES = [
    'https://www.googleapis.com/auth/drive'
    ,'https://www.googleapis.com/auth/spreadsheets']
#FOLDERS ID
SOURCE_ROOT_FOLDER_ID = "SOURCE_ROOT_FOLDER_ID" # Корніва папка тестового. Я вже вписал в config.py
SOURCE_AUDIO_FOLDER_ID = "SOURCE_AUDIO_FOLDER_ID" # Папка с аудіо тестовго. І це вже вписал в config.py
DESTINATION_ROOT_FOLDER_ID = "YOUR_DESTINATION_GOOGLE_ROOT_FOLDER_ID_HERE" # Папка куди все робити
#GEmini API
GENAI_API_KEY = "YOUR_API_KEY_HERE" # Ключ GenAi
GENAI_MODEL = "gemini-2.5-flash"
MIME_TYPE = "audio/mp3"
#DRIVE
DESTINATIO_AUDIO_FOLDER_NAME = "Records" # Назва нової папки зі звуками і транскрібуцієй
#SHEET
SHEET_NAME = "Звіт проослухованних розмов" # Назва таблиці з результатами
HIDE_CONVERSATION_WITHOUT_NAME = False # Не вписувати записи де менеджер не називає свого ім'я. True - не вписувати, False - вписувати всі записи.
```
5. Запуск
```shell
python main.py
```

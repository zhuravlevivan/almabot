import asyncio
import gzip
import shutil
import sqlite3 as sq

from datetime import datetime
from config import google_json, folder_id, scope_gdrive

from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build

base = None

SCOPES = [scope_gdrive]
SERVICE_ACCOUNT_FILE = (str(google_json))
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)


async def backup_db():
    global base
    base = sq.connect('database/users.db', check_same_thread=False)
    b_conn = sq.connect("database/backup.db")
    base.backup(b_conn)
    b_conn.close()

    await asyncio.sleep(1)

    with open('database/backup.db', 'rb') as f_in:
        with gzip.open('database/backup.db.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    await asyncio.sleep(1)

    folder = folder_id
    name = 'backup-' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.gz'
    file_path = 'database/backup.db.gz'

    file_metadata = {
                    'name': name,
                    'parents': [folder]
                    }

    media = MediaFileUpload(file_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()


async def scheduled_function():
    """
    Функция-планировщик бэкапа. Ежедневно в 0:00
    """
    current_time = datetime.now().time()
    if datetime.now().time().hour != 0:
        seconds_to_start = 86400 - (current_time.hour * 3600 + current_time.minute * 60 + current_time.second)
        await asyncio.sleep(seconds_to_start)
    
    await backup_db()
    
    await asyncio.sleep(86400)
    await scheduled_function()

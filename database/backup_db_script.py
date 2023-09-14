import asyncio
import gzip
import shutil
import sqlite3 as sq

from datetime import datetime
from config import google_json, folder_id

from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build

base = None

SCOPES = ['https://www.googleapis.com/auth/drive']
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
    name = 'backup-' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.db'
    file_path = 'database/backup.db'

    file_metadata = {
                    'name': name,
                    'parents': [folder]
                    }

    media = MediaFileUpload(file_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
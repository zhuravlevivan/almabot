import os
import dotenv

dotenv.load_dotenv()

ADMINS = os.getenv('ADMINS')

FILES = os.listdir('files/')



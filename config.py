import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("URL")
port = int(os.getenv("PORT"))
username = os.getenv("ELASTIC")
password = os.getenv("PASSWORD")

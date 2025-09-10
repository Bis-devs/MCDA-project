from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB")             # ✅ mora obstajati
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

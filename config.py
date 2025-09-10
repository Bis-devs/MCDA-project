from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = "mongodb+srv://mcda_user:2cYcxf9JECgU1JmY@clustermcda.sgqrylz.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMCDA"
DB_NAME = os.getenv("MONGO_DB")             # ✅ mora obstajati
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

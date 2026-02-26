from decouple import config

# Bot token

BOT_TOKEN = config("BOT_TOKEN")

# Database settings

DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST", default="localhost")
DB_PORT = config("DB_PORT", default="5432")
DB_NAME = config("DB_NAME")
import os

MONGO = "mongo"
ORACLE = "oracle"
ZODB = "zodb"

ACTIVE_DB = os.getenv("ACTIVE_DB", MONGO)

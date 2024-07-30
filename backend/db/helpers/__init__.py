import os
import sys
import logging
import psycopg2
from psycopg2 import pool

from logger import log_red

# getting credentials to access the database, default values provided if they are not set
USER = os.environ.get("POSTGRES_USER", "postgres")
PASSWORD = os.environ.get("POSTGRES_PASSWORD", "1234567890")
DB_NAME = os.environ.get("POSTGRES_DB", "dream")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
MIN_CONN = int(os.environ.get("POSTGRES_MINCONN", "1"))
MAX_CONN = int(os.environ.get("POSTGRES_MAXCONN", "10"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    user=USER,
    password=PASSWORD,
    database=DB_NAME,
    host="host.docker.internal",
    port=DB_PORT
)

def connect() -> psycopg2.extensions.connection:
    """
    Gets a database connection from pool
    """
    try:
        conn = connection_pool.getconn()
        return conn
    except psycopg2.Error as err:
        log_red(f"Database connection error: {err}")
        sys.exit(1)

def disconnect(conn: psycopg2.extensions.connection):
    """
    Release the database connection after use back to the pool
    """
    connection_pool.putconn(conn)

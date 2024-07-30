import asyncio
import os
from typing import Literal, List, Tuple, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg2 import Error

from db.helpers import connect, disconnect
from db.linker import DatabaseSetup
from functionality.voucher_scheduler import VoucherScheduler
from router import customer, eatery, voucher, auth, other

async def trigger_voucher_creation():
    """
    Triggers the voucher creation operation in the voucher schedular
    """
    VoucherScheduler().trigger_voucher_creation()

async def voucher_creation_task():
    """
    Schedules the voucher creation operation to occur every 30 seconds
    """
    while True:
        asyncio.create_task(trigger_voucher_creation())
        await asyncio.sleep(int(os.getenv("SCHEDULER_REPEAT_SECONDS", "30")))

@asynccontextmanager
async def lifespan(app: FastAPI): # pylint: disable=W0621
    """
    Runs startup and shutdown logic of the app
    """
    # Preload
    asyncio.create_task(voucher_creation_task())
    yield
    # Clean Up

app = FastAPI(
    title="Chowdown App",
    version="3.0.0",
    lifespan=lifespan
)

origins = [
    "http://host.docker.internal",
    "http://host.docker.internal:8080",
    "http://host.docker.internal:8000",
    "http://host.docker.internal:3000",
    "http://host.docker.internal:3001",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
]

# https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(eatery.router, prefix="/eatery", tags=["eatery"])
app.include_router(voucher.router, prefix="/voucher", tags=["voucher"])
app.include_router(customer.router, prefix="/customer", tags=["customer"])
app.include_router(other.router, prefix="/other", tags=["other"])

@app.get("/")
async def root():
    """
    Root api, currently used for example and testing
    """
    return {"message": "Hello, welcome to Chowdown"}

################################################################################
#############################   Debugging Routes   #############################
################################################################################

AllTables = Literal[
  "eateries",
  "eatery_details",
  "addresses",
  "keywords",
  "eatery_atoms",
  "customers",
  "preferences",
  "customer_likes",
  "voucher_templates",
  "vouchers",
  "voucher_instances",
  "favourite_eateries",
  "blocked_eateries",
  "favourite_customers",
  "blocked_customers",
  "passwords",
  "all_sessions",
  "reviews",
  "reports"
]

@app.get("/db/test")
async def test_database():
    """
    Test the database connection
    """
    try:
        conn = connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 100;")
                return cur.fetchone()

        except Exception as e:
            raise e
    except Error as err:
        raise err
    finally:
        disconnect(conn)

@app.get("/db/list")
async def list_all_database_tables() -> List[str]:
    """
    list all db tables
    """
    db_setup = DatabaseSetup()
    return db_setup.list_tables()

@app.delete("/db/clear")
async def clear_database_table(table: AllTables):
    """
    clear db tables
    """
    db_setup = DatabaseSetup()
    return db_setup.clear_tables([table])

@app.delete("/db/clear/all")
async def clear_all_database_tables():
    """
    clear all db tables
    """
    db_setup = DatabaseSetup()
    tables = db_setup.list_tables()
    return db_setup.clear_tables(tables)

@app.get("/table/{table_name}")
async def view_table_entries(table_name: AllTables) -> Optional[List[Tuple]]:
    """
    view the entries in table
    """
    db_setup = DatabaseSetup()
    return db_setup.view_table(table_name)

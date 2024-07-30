import os
import pytest

from functionality.voucher_scheduler import VoucherScheduler

@pytest.fixture()
def reset_db():
    """
    Used for resetting the testing database each test
    """
    from db.linker import DatabaseSetup # pylint: disable=import-outside-toplevel

    DatabaseSetup().clear_tables(DatabaseSetup().list_tables())
    VoucherScheduler().reset_scheduler()

@pytest.fixture(autouse=True)
def setup():
    """
    Sets up environment variables for each test
    """
    os.environ["REFRESH_TOKEN_SECRET"] = "DreamTeamH18A"
    os.environ["REFRESH_TOKEN_EXPIRY_DAYS"] = "7"

    os.environ["ACCESS_TOKEN_SECRET"] = "ThisIsADummyKey"
    os.environ["ACCESS_TOKEN_EXPIRY_MINUTES"] = "15"

    os.environ["SCHEDULER_REPEAT_SECONDS"] = "30"

    os.environ["SMART_SEARCH"] = "False"
    os.environ["OPENAI_API_KEY"] = "NotReal"

import calendar

from datetime import datetime, timedelta, timezone
from threading import Lock
from queue import PriorityQueue
from typing import Optional

from logger import log_purple

from functionality.errors import ValidationError

from db.db_types.db_request import VoucherCreationRequest, VoucherInstanceCreationRequest
from db.helpers.voucher import insert_voucher
from db.helpers.voucher_instance import insert_voucher_instance
from db.helpers.voucher_template import get_all_voucher_templates, get_voucher_template_schedule_by_id, update_voucher_template_last_release

class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class VoucherScheduler(metaclass=SingletonMeta):
    def __init__(self):
        log_purple("Initialising Voucher Scheduler")

        # This should hold the release date of the next batch of vouchers and the voucher template id
        self.queue = PriorityQueue()

        self._initialise_queue()
        log_purple("Voucher Scheduler initialised")

    def _initialise_queue(self):
        """
        Initialises the queue with all voucher templates
        """
        # Go through and get all voucher templates
        voucher_template_ids = get_all_voucher_templates()

        if voucher_template_ids is None:
            raise ValidationError("No voucher templates found")

        for voucher_template_id in voucher_template_ids:
            self.add_voucher(voucher_template_id)

    def _get_voucher_template_next_release(self, voucher_template_id: int) -> Optional[datetime]:
        """
        Takes in the id for a voucher_template and determines the next release date for the batch of vouchers
        """
        voucher_template = get_voucher_template_schedule_by_id(voucher_template_id)

        if voucher_template is None:
            raise ValidationError("Voucher template not found")

        # If voucher template is deleted, don't schedule
        if voucher_template.is_deleted:
            return None

        if voucher_template.last_release is None:
            return voucher_template.release_date

        # This voucher is only meant to be issued once
        # And we have alrdy issued it in this case
        if voucher_template.release_schedule is None:
            return None

        def get_next_time(start, prev_end, step):
            next_time = start

            while next_time < prev_end:
                next_time += step

            return next_time
        
        def release_schedule_time_handler(release_schedule: str, release_date: datetime, last_release: datetime):
            if release_schedule == "daily":
                return get_next_time(release_date, last_release, timedelta(days=1))
            if release_schedule == "weekly":
                return get_next_time(release_date, last_release, timedelta(weeks=1))
            if release_schedule == "fortnightly":
                return get_next_time(release_date, last_release, timedelta(weeks=2))
            if release_schedule == "monthly":
                # This case is a little bit more difficult to handle
                # We want to make sure it's on the same date as the release date

                # Get the day of the month
                release_day = release_date.day
                release_month = release_date.month
                release_year = release_date.year

                _, last_day = calendar.monthrange(release_year, release_month)

                # If the release day is greater than the last day of the month, we need to move it to the last day
                release_day = min(release_day, last_day)

                return datetime(release_year, release_month, release_day)

            raise ValidationError("Invalid release schedule")

        return release_schedule_time_handler(voucher_template.release_schedule, voucher_template.release_date, voucher_template.last_release)

    def add_voucher(self, voucher_template_id: int):
        """
        A method for adding a voucher to the priority queue
        """
        # Get the vouchers next release date
        release_date = self._get_voucher_template_next_release(voucher_template_id)

        if release_date is None:
            return

        # Add to the queue ordering by release_date
        self.queue.put((release_date, voucher_template_id))

    def trigger_voucher_creation(self):
        """
        Used to trigger the creation of vouchers
        """
        self._create_voucher_batches()
        self._log_voucher_queue()

    def _log_voucher_queue(self):
        """
        Logs the current state of the queue
        """
        temp = self.queue.queue.copy()

        log_purple(f"Voucher Scheduler: Size={len(temp)}")
        for item in temp:
            log_purple(f"Voucher Scheduler: Release Date=\"{item[0]}\", Voucher Template ID=\"{item[1]}\"")

    def _create_voucher_batches(self):
        """
        Creates the vouchers for templates that are scheduled to be created
        """
        log_purple("Voucher Scheduler creating voucher batches")

        # Get the current time
        current_time = datetime.now(timezone.utc)

        # Used for logging
        vouchers_created = 0

        # While there are vouchers to be created
        while not self.queue.empty():
            # Get the next voucher to be created
            release_date, voucher_template_id = self.queue.get()

            # If the release date is in the future, we can stop
            if release_date > current_time:
                self.queue.put((release_date, voucher_template_id))
                break

            self._create_voucher(voucher_template_id, release_date)
            vouchers_created += 1

            # Add the next batch of vouchers to the queue
            self.add_voucher(voucher_template_id)

        log_purple(f"Voucher Scheduler done creating voucher batches. Created=\"{vouchers_created}\"")

    def _create_voucher(self, voucher_template_id: int, release_date: datetime) -> int:
        """
        Creates a voucher for the voucher template
        """
        voucher_template = get_voucher_template_schedule_by_id(voucher_template_id)

        if voucher_template is None:
            raise ValidationError("Voucher template not found")

        # Create the voucher
        voucher = VoucherCreationRequest(
            voucher_template=voucher_template_id,
            release_date=release_date,
            expiry_date=release_date + voucher_template.release_duration
        )

        release_time = datetime.now(timezone.utc)

        v_id = insert_voucher(voucher)

        if v_id is None:
            raise ValidationError("Error creating voucher")

        insert_voucher_instance(VoucherInstanceCreationRequest(
            status=("unclaimed"),
            voucher=v_id,
            qty=voucher_template.release_size
        ))

        update_voucher_template_last_release(voucher_template_id, release_time)

        return v_id

    def reset_scheduler(self):
        """
        Resets and restarts the scheduler

        Clears all data inside of it
        """
        self.__init__()

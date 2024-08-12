from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.api.database.config import get_db
from app.api.utils.ebay_scrape import ParseEbayListing
from app.scheduler.tasks.check_and_mail import check_all_listings_and_mail

scheduler = BackgroundScheduler()


db = next(get_db())
parser = ParseEbayListing()


scheduler.add_job(
    check_all_listings_and_mail,
    CronTrigger.from_crontab("0 7 * * *"),
    id="check_and_mail",
    replace_existing=True,
    args=[db, parser],
)

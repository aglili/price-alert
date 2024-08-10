from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.scheduler.tasks.check_and_mail import check_all_listings_and_mail

scheduler = BackgroundScheduler()


scheduler.add_job(
    check_all_listings_and_mail,
    CronTrigger.from_crontab("0 7 * * *"),
    id='check_and_mail', 
    replace_existing=True
)
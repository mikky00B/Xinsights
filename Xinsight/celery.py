from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Xinsight.settings")


app = Celery("Xinsight")

# Load task modules from all registered Django app configs
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "fetch-twitter-data-every-hour": {
        "task": "nalytics.tasks.fetch_twitter_data",
        "schedule": 3600.0,
        "args": ("clevermike_a",),
    },
    "like_recent_tweets": {
        "task": "your_app.tasks.like_recent_tweets",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
        "args": ("clevermike_a",),
    },
    "retweet_recent_tweets": {
        "task": "your_app.tasks.retweet_recent_tweets",
        "schedule": crontab(minute="*/30"),
        "args": ("clevermike_a",),
    },
    "reply_to_mentions": {
        "task": "your_app.tasks.reply_to_recent_mentions",
        "schedule": crontab(minute="*/60"),  # Every hour
        "args": ("clevermike_a", "Thank you for mentioning me!"),
    },
}

from celery import Celery
from celery.schedules import crontab

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.Parsing.tasks"]  # Добавить "app." перед "Parsing"
)

celery.autodiscover_tasks(["app.Parsing"])

celery.conf.beat_schedule = {
    "run-parser-every-day": {
        "task": "app.Parsing.tasks.run_games_list_parser",
        "schedule": crontab(hour=9, minute=40),
    },
}

celery.conf.timezone = "Asia/Yekaterinburg"




#              celery -A app.celery worker --loglevel=debug
#              celery -A app worker --loglevel=debug --pool=solo
#              "D:\VSC Projects\App\env\Scripts\python" -m celery -A app.celery worker --loglevel=info --pool=solo
#              celery -A app.celery beat --loglevel=info

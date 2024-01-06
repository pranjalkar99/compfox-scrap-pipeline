from celery import Celery

celery_task = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    include=["v2_pipeline.process"],
)
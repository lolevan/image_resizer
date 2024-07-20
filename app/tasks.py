from celery import Celery
from .services import process_image

celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)


@celery.task
def process_image_task(input_path, output_path, width, height, quality, watermark_path, position, transparency):
    process_image(input_path, output_path, width, height, quality, watermark_path, position, transparency)
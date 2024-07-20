from celery import Celery
from .services import process_image
import logging

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('image_processing.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

@celery.task
def process_image_task(input_path, output_path, width, height, quality, watermark_path, position, transparency):
    logger.info("Starting image processing task")
    try:
        process_image(input_path, output_path, width, height, quality, watermark_path, position, transparency)
        logger.info(f"Image processed and saved to {output_path}")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")

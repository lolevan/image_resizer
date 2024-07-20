from PIL import Image, ImageEnhance
import os
import logging

# Настройка логгера
logger = logging.getLogger(__name__)


def process_image(input_path, output_path, width, height, quality, watermark_path, position, transparency):
    try:
        with Image.open(input_path) as img:
            logger.info(f"Original image size: {img.size}")
            if width and height:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            elif width:
                ratio = width / float(img.size[0])
                height = int(float(img.size[1]) * ratio)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            elif height:
                ratio = height / float(img.size[1])
                width = int(float(img.size[0]) * ratio)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            logger.info(f"Resized image size: {img.size}")

            if watermark_path:
                with Image.open(watermark_path) as watermark:
                    logger.info(f"Original watermark size: {watermark.size}")
                    # Проверка и изменение размера водяного знака
                    if watermark.size[0] > img.size[0] or watermark.size[1] > img.size[1]:
                        ratio = min(img.size[0] / float(watermark.size[0]), img.size[1] / float(watermark.size[1]))
                        new_size = (int(watermark.size[0] * ratio), int(watermark.size[1] * ratio))
                        watermark = watermark.resize(new_size, Image.Resampling.LANCZOS)
                    logger.info(f"Resized watermark size: {watermark.size}")

                    if transparency < 255:
                        alpha = watermark.split()[3]
                        alpha = ImageEnhance.Brightness(alpha).enhance(transparency / 255.0)
                        watermark.putalpha(alpha)

                    # Позиционирование водяного знака
                    if position == 'center':
                        position = (
                            (img.size[0] - watermark.size[0]) // 2,
                            (img.size[1] - watermark.size[1]) // 2
                        )

                    img.paste(watermark, position, watermark)

            img.save(output_path, quality=quality)
            logger.info(f"Saved processed image to {output_path}")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
    finally:
        os.remove(input_path)
        if watermark_path:
            os.remove(watermark_path)

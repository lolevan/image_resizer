from PIL import Image, ImageEnhance, ImageSequence
import os
import logging

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('image_processing.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def process_image(input_path, output_path, width, height, quality, watermark_path, position, transparency):
    try:
        with Image.open(input_path) as img:
            logger.info(f"Original image size: {img.size}")
            if img.format == 'GIF' and img.is_animated:
                frames = []
                for frame in ImageSequence.Iterator(img):
                    frame = frame.convert("RGBA")
                    frame = process_single_frame(frame, width, height, watermark_path, position, transparency)
                    frames.append(frame)

                frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0)
            else:
                img = process_single_frame(img, width, height, watermark_path, position, transparency)
                img.save(output_path, quality=quality)
            logger.info(f"Saved processed image to {output_path}")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
    finally:
        os.remove(input_path)
        if watermark_path:
            os.remove(watermark_path)


def process_single_frame(frame, width, height, watermark_path, position, transparency):
    if width and height:
        frame = frame.resize((width, height), Image.Resampling.LANCZOS)
    elif width:
        ratio = width / float(frame.size[0])
        height = int(float(frame.size[1]) * ratio)
        frame = frame.resize((width, height), Image.Resampling.LANCZOS)
    elif height:
        ratio = height / float(frame.size[1])
        width = int(float(frame.size[0]) * ratio)
        frame = frame.resize((width, height), Image.Resampling.LANCZOS)

    logger.info(f"Resized image size: {frame.size}")

    if watermark_path:
        with Image.open(watermark_path) as watermark:
            logger.info(f"Original watermark size: {watermark.size}")
            # Проверка и изменение размера водяного знака
            if watermark.size[0] > frame.size[0] or watermark.size[1] > frame.size[1]:
                ratio = min(frame.size[0] / float(watermark.size[0]), frame.size[1] / float(watermark.size[1]))
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
                    (frame.size[0] - watermark.size[0]) // 2,
                    (frame.size[1] - watermark.size[1]) // 2
                )

            frame.paste(watermark, position, watermark)

    return frame

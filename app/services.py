from PIL import Image, ImageEnhance
import os


def process_image(input_path, output_path, width, height, quality, watermark_path, position, transparency):
    try:
        with Image.open(input_path) as img:
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

            if watermark_path:
                with Image.open(watermark_path) as watermark:
                    if transparency < 255:
                        alpha = watermark.split()[3]
                        alpha = ImageEnhance.Brightness(alpha).enhance(transparency / 255.0)
                        watermark.putalpha(alpha)
                    img.paste(watermark, (0, 0), watermark)

            img.save(output_path, quality=quality)
    finally:
        os.remove(input_path)
        if watermark_path:
            os.remove(watermark_path)






from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from .tasks import process_image_task
from .enums import WatermarkPosition
import shutil
import os
import uuid

router = APIRouter()

TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../temp')


@router.post("/process_image/")
async def resize_image(
    image: UploadFile = File(...),
    width: int = Form(None),
    height: int = Form(None),
    quality: int = Form(85),
    watermark: UploadFile = File(None),
    position: WatermarkPosition = Form(WatermarkPosition.center),
    transparency: int = Form(128)
):
    try:
        image_id = str(uuid.uuid4())
        temp_image_path = os.path.join(TEMP_DIR, f"{image_id}_{image.filename}")
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        watermark_path = None
        if watermark:
            watermark_id = str(uuid.uuid4())
            watermark_path = os.path.join(TEMP_DIR, f"{watermark_id}_{watermark.filename}")
            with open(watermark_path, "wb") as buffer:
                shutil.copyfileobj(watermark.file, buffer)

        output_path = os.path.join(TEMP_DIR, f"processed_{image_id}_{image.filename}")
        process_image_task.delay(temp_image_path, output_path, width, height, quality, watermark_path, position.value, transparency)
        return JSONResponse(content={"message": "Image processing started", "image_id": image_id}, status_code=202)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

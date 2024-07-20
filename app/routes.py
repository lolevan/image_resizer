from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from .services import process_image
from .tasks import process_image_task
import shutil
import os
import uuid

router = APIRouter()


@router.post("/process_image/")
async def resize_image(
        image: UploadFile = File(...),
        width: int = Form(...),
        height: int = Form(...),
        quality: int = Form(85),
        watermark: UploadFile = File(None),
        position: str = Form("center"),
        transparency: int = Form(128),
):
    try:
        image_id = str(uuid.uuid4())
        temp_image_path = f"tmp/{image_id}_{image.filename}"
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        watermark_path = None
        if watermark:
            watermark_id = str(uuid.uuid4())
            watermark_path = f"tmp/{watermark_id}_{watermark.filename}"
            with open(watermark_path, "wb") as buffer:
                shutil.copyfileobj(watermark.file, buffer)

        output_path = f"/tmp/processed_{image_id}_{image.filename}"
        process_image_task.delay(temp_image_path, output_path, width, height, quality, watermark_path, position, transparency)
        return JSONResponse(content={"message": "Image processing started", "image_id": image_id}, status_code=202)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

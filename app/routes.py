from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Security, Request
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from sqlalchemy.orm import Session

from .config import validate_api_key

from .models import APIKey, Base, engine

from .dependencies import get_db

from .tasks import process_image_task

from .enums import WatermarkPosition

import shutil

import uuid

import secrets

import os


router = APIRouter()

TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../temp')

Base.metadata.create_all(bind=engine)

api_key_header = APIKeyHeader(name='Authorization')


@router.post("/create_key/")
async def create_api_key(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user = data.get('user')
    if not user:
        raise HTTPException(status_code=400, detail="User name is required")
    key = secrets.token_hex(16)
    db_key = APIKey(key=key, user=user)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return {"api_key": db_key.key}


@router.get("/get_keys/")
async def get_api_keys(db: Session = Depends(get_db)):
    return db.query(APIKey).all()


async def get_api_key(
        api_key: str = Security(api_key_header),
        db: Session = Depends(get_db)
):
    if not validate_api_key(api_key, db):
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )
    return api_key


@router.post("/process_image/")
async def resize_image(
    api_key: str = Security(get_api_key),
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

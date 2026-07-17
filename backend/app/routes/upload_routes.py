from fastapi import APIRouter, UploadFile, File

from app.services.upload_service import save_image

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/")
def upload_image(file: UploadFile = File(...)):
    image_url = save_image(file)

    return {
        "message": "Image uploaded successfully.",
        "image_url": image_url
    }
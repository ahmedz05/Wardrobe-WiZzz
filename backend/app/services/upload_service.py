import os
import uuid
from fastapi import UploadFile, HTTPException

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


def save_image(file: UploadFile):

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed."
        )

    filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as image:
        image.write(file.file.read())

    return f"/uploads/{filename}"
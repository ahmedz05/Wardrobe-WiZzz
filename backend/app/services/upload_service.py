from pathlib import Path
import uuid

from fastapi import HTTPException, UploadFile


# backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]

# backend/uploads/
UPLOAD_FOLDER = BACKEND_DIR / "uploads"

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def save_image(file: UploadFile):
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed.",
        )

    filename = f"{uuid.uuid4()}{extension}"

    file_path = UPLOAD_FOLDER / filename

    with open(file_path, "wb") as image:
        image.write(file.file.read())

    return f"/uploads/{filename}"
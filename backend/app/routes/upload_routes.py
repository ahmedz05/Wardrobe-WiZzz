from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/", status_code=503)
async def upload_image() -> None:
    """Fail closed until uploads have validated content and trusted ownership.

    Do not declare File/UploadFile dependencies here: multipart parsing and disk
    spooling would happen before this rejection. Existing files are left intact.
    """
    raise HTTPException(
        status_code=503,
        detail="Wardrobe image uploads are temporarily unavailable.",
        headers={"Cache-Control": "no-store"},
    )

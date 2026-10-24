from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.services.auth_dependencies import (
    get_current_user,
)

from app.services.outfit_generation_service import (
    generate_outfits,
)


router = APIRouter(
    prefix="/outfits",
    tags=["Outfits"],
)


@router.get("/generate")
def generate_user_outfits(
    limit: int = Query(
        default=5,
        ge=1,
        le=20,
    ),
    include_layers: bool = Query(
        default=True,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    try:
        return generate_outfits(
            db=db,
            user_id=current_user.id,
            limit=limit,
            include_layers=include_layers,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
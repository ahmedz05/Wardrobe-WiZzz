
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

from app.services.weather_provider_service import (
    get_current_weather,
    get_weather_by_coordinates,
    WeatherProviderError,
)


router = APIRouter(
    prefix="/outfits",
    tags=["Outfits"],
)


@router.get("/generate")
async def generate_user_outfits(
    limit: int = Query(
        default=5,
        ge=1,
        le=20,
    ),

    include_layers: bool = Query(
        default=True,
    ),

    location: str | None = Query(
        default=None,
        min_length=2,
        max_length=120,
        description="Optional city name.",
    ),

    latitude: float | None = Query(
        default=None,
        ge=-90,
        le=90,
        description="Device latitude.",
    ),

    longitude: float | None = Query(
        default=None,
        ge=-180,
        le=180,
        description="Device longitude.",
    ),

    temperature_c: float | None = Query(
        default=None,
        ge=-30,
        le=60,
    ),

    condition: str | None = Query(
        default=None,
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):
    """
    Generate outfits using:

    1. Device coordinates
    2. A manually selected city
    3. Manually specified weather
    4. Fashion compatibility only

    Location coordinates are used for this
    request and are not saved to the database.
    """

    has_latitude = latitude is not None
    has_longitude = longitude is not None

    if has_latitude != has_longitude:
        raise HTTPException(
            status_code=400,
            detail=(
                "Both latitude and longitude "
                "must be provided together."
            ),
        )

    has_coordinates = (
        has_latitude and has_longitude
    )

    has_location = location is not None

    has_manual_weather = (
        temperature_c is not None
        or condition is not None
    )

    selected_sources = sum([
        has_coordinates,
        has_location,
        has_manual_weather,
    ])

    if selected_sources > 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "Use only one weather source: "
                "coordinates, city, or manual weather."
            ),
        )

    if condition is not None and temperature_c is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "temperature_c is required "
                "when condition is provided."
            ),
        )

    live_weather = None

    try:
        if has_coordinates:
            weather_data = (
                await get_weather_by_coordinates(
                    latitude=latitude,
                    longitude=longitude,
                )
            )

            live_weather = {
                "provider": "Open-Meteo",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "weather": weather_data,
            }

        elif has_location:
            live_weather = (
                await get_current_weather(
                    location=location
                )
            )

        if live_weather is not None:
            weather_data = live_weather["weather"]

            temperature_c = weather_data.get(
                "temperature_c"
            )

            condition = weather_data.get(
                "condition"
            )

            if temperature_c is None:
                raise WeatherProviderError(
                    "Weather provider returned "
                    "no usable temperature."
                )

    except WeatherProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    try:
        result = generate_outfits(
            db=db,
            user_id=current_user.id,
            limit=limit,
            include_layers=include_layers,
            temperature_c=temperature_c,
            condition=condition,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    result["weather_source"] = live_weather

    return result

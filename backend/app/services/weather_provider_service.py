# app/services/weather_provider_service.py

import httpx


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Cloudy",

    45: "Fog",
    48: "Fog",

    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",

    56: "Freezing Drizzle",
    57: "Freezing Drizzle",

    61: "Rain",
    63: "Rain",
    65: "Heavy Rain",

    66: "Freezing Rain",
    67: "Freezing Rain",

    71: "Snow",
    73: "Snow",
    75: "Heavy Snow",

    77: "Snow",

    80: "Showers",
    81: "Showers",
    82: "Heavy Showers",

    85: "Snow Showers",
    86: "Snow Showers",

    95: "Thunderstorm",

    96: "Thunderstorm",
    99: "Thunderstorm",
}


class WeatherProviderError(Exception):
    """
    Raised when external weather data
    cannot be retrieved or interpreted.
    """

    pass


async def geocode_location(
    location: str,
) -> dict:
    """
    Convert a human-readable location
    into latitude and longitude.
    """

    cleaned_location = location.strip()

    if not cleaned_location:
        raise WeatherProviderError(
            "Location cannot be empty."
        )

    params = {
        "name": cleaned_location,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:
        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:
            response = await client.get(
                GEOCODING_URL,
                params=params,
            )

            response.raise_for_status()

    except httpx.HTTPError as exc:
        raise WeatherProviderError(
            "Could not reach the weather "
            "geocoding service."
        ) from exc

    data = response.json()

    results = data.get(
        "results",
        [],
    )

    if not results:
        raise WeatherProviderError(
            f"No location found for "
            f"'{cleaned_location}'."
        )

    result = results[0]

    return {
        "name": result.get(
            "name"
        ),

        "country": result.get(
            "country"
        ),

        "admin1": result.get(
            "admin1"
        ),

        "latitude": result[
            "latitude"
        ],

        "longitude": result[
            "longitude"
        ],

        "timezone": result.get(
            "timezone"
        ),
    }


async def get_weather_by_coordinates(
    latitude: float,
    longitude: float,
) -> dict:
    """
    Retrieve current weather from
    Open-Meteo using coordinates.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:
            response = await client.get(
                FORECAST_URL,
                params=params,
            )

            response.raise_for_status()

    except httpx.HTTPError as exc:
        raise WeatherProviderError(
            "Could not retrieve current "
            "weather data."
        ) from exc

    data = response.json()

    current = data.get(
        "current"
    )

    if current is None:
        raise WeatherProviderError(
            "Weather provider returned no "
            "current weather data."
        )

    weather_code = current.get(
        "weather_code"
    )

    condition = (
        WEATHER_CODE_DESCRIPTIONS.get(
            weather_code,
            "Unknown",
        )
    )

    return {
        "temperature_c": current.get(
            "temperature_2m"
        ),

        "apparent_temperature_c": (
            current.get(
                "apparent_temperature"
            )
        ),

        "condition": condition,

        "weather_code": weather_code,

        "precipitation_mm": current.get(
            "precipitation"
        ),

        "wind_speed_kmh": current.get(
            "wind_speed_10m"
        ),

        "observed_at": current.get(
            "time"
        ),

        "timezone": data.get(
            "timezone"
        ),
    }


async def get_current_weather(
    location: str,
) -> dict:
    """
    Resolve a location and retrieve
    its current weather.

    This function is the main interface
    used by Wardrobe-WIZzz.

    The rest of the application does not
    need to know which external weather
    provider is being used.
    """

    resolved_location = (
        await geocode_location(
            location
        )
    )

    weather = (
        await get_weather_by_coordinates(
            latitude=resolved_location[
                "latitude"
            ],
            longitude=resolved_location[
                "longitude"
            ],
        )
    )

    return {
        "provider": "Open-Meteo",

        "location": {
            "name": resolved_location[
                "name"
            ],

            "admin1": resolved_location[
                "admin1"
            ],

            "country": resolved_location[
                "country"
            ],

            "latitude": resolved_location[
                "latitude"
            ],

            "longitude": resolved_location[
                "longitude"
            ],
        },

        "weather": weather,
    }
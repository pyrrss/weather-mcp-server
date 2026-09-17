from typing import Any
import logging

import httpx2
from mcp.server import MCPServer


logger = logging.getLogger(__name__)


mcp = MCPServer()


FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
TIMEZONE = "America/Santiago"


async def get_json(url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """
    Hace una request HTTP GET a la API de Open-Meteo y devuelve el JSON.
    """
    async with httpx2.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error obteniendo datos de clima: {e}")
            return None


# -- TOOLS --
@mcp.tool()
async def search_location(city: str) -> str:
    """
    Busca una ubicación por nombre y devuelve sus coordenadas.

    Args:
        city (str): Nombre de la ciudad (e.g. "Santiago", "Valparaíso").

    """
    params = {"name": city, "count": 5, "language": "es", "countryCode": "CL"}
    data = await get_json(GEOCODING_URL, params)

    if not data or not data.get("results"):
        return f"No se encontró ninguna ubicación en Chile para '{city}'."

    results = []
    for result in data["results"]:
        location = (
            f"{result['name']} ({result.get('admin1', '')}, {result.get('country', '')}): "
            f"lat {result['latitude']}, lon {result['longitude']}"
        )
        results.append(location)

    return "\n".join(results)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Obtiene el pronóstico del clima para una ubicación específica usando Open-Meteo.

    Args:
        latitude (float): Latitud de la ubicación.
        longitude (float): Longitud de la ubicación.

    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": TIMEZONE,
        "forecast_days": 7,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
    }
    data = await get_json(FORECAST_URL, params)

    if not data:
        return "No se pudo obtener el pronóstico del clima para la ubicación especificada."

    forecasts = []

    current = data.get("current", {})
    if current:
        current_forecast = (
            "Condiciones actuales:\n"
            f"Temperatura: {current['temperature_2m']}°C\n"
            f"Humedad: {current.get('relative_humidity_2m', '-')}%\n"
            f"Viento: {current.get('wind_speed_10m', '-')} km/h\n"
            f"Precipitación: {current.get('precipitation', '-')} mm"
        )
        forecasts.append(current_forecast)

    daily = data.get("daily", {})
    days = daily.get("time", [])
    for index in range(len(days)):
        forecast = f"""
        {days[index]}:
        Temperatura: {daily['temperature_2m_min'][index]}°C / {daily['temperature_2m_max'][index]}°C
        Precipitación: {daily['precipitation_sum'][index]} mm
        Viento máx: {daily['wind_speed_10m_max'][index]} km/h
        """
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    mcp.run(transport="stdio")

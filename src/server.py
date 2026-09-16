from typing import Any
import logging

import httpx2
from mcp.server import MCPServer


logger = logging.getLogger(__name__)


mcp = MCPServer()


NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# -- HELPERS --
async def get_weather_data(url: str) -> dict[str, Any] | None:
    """
    Hace una request HTTP a API NWS para obtener datos de clima.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx2.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Error obteniendo datos de clima: {e}")
            return None

def format_alert(feature: dict) -> str:
    """
    Formatea una alerta de clima en un string legible.
    """
    properties = feature["properties"]
    return f"""
    Alerta: {properties.get("event", "Desconocida")}
    Area: {properties.get("areaDesc", "Desconocida")}
    Severidad: {properties.get("severity", "Desconocida")}
    Descripción: {properties.get("description", "No disponible")}
    Instrucciones: {properties.get("instruction", "No disponible")}
    """


# -- TOOLS --
@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    Obtiene alertas de clima para un estado específico de EE.UU usando API de NWS.

    Args:
        state (str): Código de dos letras del estado (e.g. CA, NY)

    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await get_weather_data(url)
    
    if not data or "features" not in data:
        return f"No se pudieron obtener alertas para el estado {state}."
    
    if not data["features"]:
        return f"No hay alertas activas para el estado {state}."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Obtiene pronóstico del clima para una ubicación específica usando API de NWS.
    
    Args:
        latitude (float): Latitud de la ubicación.
        longitude (float): Longitud de la ubicación.
    """
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await get_weather_data(points_url)
    
    if not points_data:
        return "No se pudo obtener información de pronóstico para la ubicación especificada."

    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await get_weather_data(forecast_url)

    if not forecast_data:
        return "No se pudo obtener el pronóstico del clima"

    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods:
        forecast = f"""
        {period['name']}:
        Temperatura: {period['temperature']}°{period['temperatureUnit']}
        Viento: {period['windSpeed']} {period['windDirection']}
        Pronóstico: {period['detailedForecast']}
        """
        forecasts.append(forecast)
    
    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    mcp.run(transport="stdio")

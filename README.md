# mcp-project

Servidor MCP de clima basado en [Open-Meteo](https://open-meteo.com/) que expone búsqueda de ubicaciones y pronóstico.

## Construir la imagen

```bash
docker build -t mcp-project:latest .
```

## Ejecutar el contenedor

```bash
docker run --rm -i mcp-project:latest
```

## Uso con opencode

> **Nota:** al ejecutar `opencode` en este directorio, el contenedor se levanta automáticamente (queda registrado como MCP local en `opencode.json`). Solo es necesario que la imagen esté construida.

## Uso como servidor MCP (stdio)

Configuración de ejemplo en `mcp-servers.json`:

```json
{
  "servers": {
    "clima": {
      "type": "stdio",
      "command": "docker run --rm -i mcp-project:latest"
    }
  }
}
```

FROM python:3.12-slim

WORKDIR /app

ENV UV_PYTHON_PREFERENCE=system
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

COPY . .
CMD ["/app/.venv/bin/mcp", "run", "src/server.py"]

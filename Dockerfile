FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY docker/skills.yaml /app/skills.yaml

RUN pip install --no-cache-dir .[mcp]

RUN mkdir -p /app/skills

VOLUME ["/app/skills"]
EXPOSE 8000

ENTRYPOINT ["python", "-m", "mcp_skill_framework"]
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000", "--path", "/mcp", "--config", "/app/skills.yaml"]

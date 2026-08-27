FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    PYTHONPATH=/app/mcp

RUN pip install --no-cache-dir --upgrade pip

COPY mcp/requirements.txt ./mcp/requirements.txt
RUN pip install --no-cache-dir -r mcp/requirements.txt pypdf

COPY . .

WORKDIR /app/mcp
ENV MODE=hosted
EXPOSE 8080

CMD ["python", "hosted.py"]

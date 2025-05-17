FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .

COPY src/ src/

CMD ["uvicorn", "chain_processor_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

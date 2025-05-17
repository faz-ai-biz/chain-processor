FROM python:3.13-slim

WORKDIR /app

# Copy and install core package
COPY chain-processor-core /app/chain-processor-core
RUN cd /app/chain-processor-core && pip install -e .

# Copy and install db package
COPY chain-processor-db /app/chain-processor-db
RUN cd /app/chain-processor-db && pip install -e .

# Copy and install API package
COPY chain-processor-api /app/chain-processor-api
WORKDIR /app/chain-processor-api
RUN pip install -e .

# Run the API server
CMD ["uvicorn", "chain_processor_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

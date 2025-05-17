FROM core-chain-nlp-base:latest

WORKDIR /app

# Copy and install API package
COPY chain-processor-api /app/chain-processor-api
WORKDIR /app/chain-processor-api
RUN pip install -e .

# Run the API server
CMD ["uvicorn", "chain_processor_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

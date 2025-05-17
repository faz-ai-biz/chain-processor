FROM python:3.13-slim

WORKDIR /app

# Copy and install db package
COPY chain-processor-db /app/chain-processor-db
RUN cd /app/chain-processor-db && pip install -e .

# Copy and install core package
COPY chain-processor-core /app/chain-processor-core
WORKDIR /app/chain-processor-core
RUN pip install -e .

# Run the core service
CMD ["python", "-m", "chain_processor_core"] 
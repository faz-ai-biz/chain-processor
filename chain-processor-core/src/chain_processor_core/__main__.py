import time
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting chain-processor-core service...")
    try:
        while True:
            logging.info("chain-processor-core service is running, sleeping for 60 seconds...")
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("chain-processor-core service stopping due to KeyboardInterrupt.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        logging.info("chain-processor-core service has stopped.")

if __name__ == "__main__":
    main() 
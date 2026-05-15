"""Mock sensor data simulator for development and testing.

This script generates fake soil moisture readings and sends them to the API.
Useful for testing without actual hardware.

Usage:
    python simulator.py

Configuration via environment variables:
    API_URL: Backend API URL (default: http://localhost:8000)
    INTERVAL: Data send interval in seconds (default: 5)
    MIN_MOISTURE: Minimum moisture value (default: 300)
    MAX_MOISTURE: Maximum moisture value (default: 800)
"""

import time
import random
import os
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === CONFIGURATION ===
API_URL = os.getenv("API_URL", "http://localhost:8000")
INTERVAL = int(os.getenv("INTERVAL", 5))
MIN_MOISTURE = int(os.getenv("MIN_MOISTURE", 300))
MAX_MOISTURE = int(os.getenv("MAX_MOISTURE", 800))
MAX_RETRIES = 3

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# === SETUP HTTP SESSION WITH RETRY LOGIC ===
session = requests.Session()
retry_strategy = Retry(
    total=MAX_RETRIES,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)


def send_sensor_data(moisture_value: int) -> bool:
    """Send mock sensor data to API.
    
    Args:
        moisture_value: Simulated moisture reading (0-1023)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        payload = {"moisture": moisture_value}
        endpoint = f"{API_URL}/sensor"
        
        response = session.post(
            endpoint,
            json=payload,
            timeout=5
        )
        
        if response.status_code in [201, 200]:
            logger.info(f"✓ Data sent: moisture={moisture_value}")
            return True
        else:
            logger.warning(f"✗ HTTP {response.status_code}: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        logger.error(f"✗ Request timeout (>{5}s) to {API_URL}")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"✗ Connection failed to {API_URL} - is the API running?")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Request error: {str(e)}")
        return False
    except ValueError as e:
        logger.error(f"✗ Invalid JSON data: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error: {str(e)}")
        return False


def simulate_sensor_reading() -> int:
    """Generate realistic mock sensor reading with slight variation.
    
    Returns:
        int: Simulated moisture value (0-1023)
    """
    base_value = random.randint(MIN_MOISTURE, MAX_MOISTURE)
    variation = random.randint(-50, 50)
    return max(0, min(1023, base_value + variation))


def main():
    """Main simulator loop."""
    logger.info("=" * 50)
    logger.info("IoT Watering System - Sensor Data Simulator")
    logger.info("=" * 50)
    logger.info(f"API URL: {API_URL}")
    logger.info(f"Send interval: {INTERVAL}s")
    logger.info(f"Moisture range: {MIN_MOISTURE}-{MAX_MOISTURE}")
    logger.info("Press Ctrl+C to stop\n")
    
    attempt_count = 0
    success_count = 0
    
    try:
        while True:
            moisture = simulate_sensor_reading()
            attempt_count += 1
            
            if send_sensor_data(moisture):
                success_count += 1
            
            if attempt_count % 10 == 0:
                success_rate = (success_count / attempt_count) * 100
                logger.info(f"Stats: {success_count}/{attempt_count} successful ({success_rate:.1f}%)")
            
            time.sleep(INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 50)
        logger.info("Simulator stopped by user")
        logger.info(f"Total: {success_count}/{attempt_count} successful")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
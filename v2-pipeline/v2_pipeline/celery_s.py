from celery import Celery

from v2_pipeline.celery_config import *
import subprocess
import time

def start_redis_server():
    try:
        # Start Redis server using subprocess
        subprocess.Popen(['redis-server'])

        # Wait for a moment to ensure Redis has started
        time.sleep(2)

        print("Redis server started successfully.")
    except Exception as e:
        print(f"Error starting Redis server: {e}")

if __name__ == "__main__":
    start_redis_server()
    celery.start()



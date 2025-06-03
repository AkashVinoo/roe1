import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Render deployment process")
    
    # Get the port from environment
    port = os.environ.get("PORT", "8000")
    logger.info(f"Port set to: {port}")
    
    # Ensure uvicorn is in path
    try:
        import uvicorn
        logger.info("Uvicorn successfully imported")
    except ImportError:
        logger.error("Uvicorn not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn"])
    
    # Start the server using Python's subprocess
    cmd = [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", port]
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
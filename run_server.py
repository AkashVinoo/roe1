import uvicorn
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log')
    ]
)
logger = logging.getLogger(__name__)

def check_prerequisites():
    """Check if all required files and models are present"""
    required_files = [
        'project1.py',
        'api.py',
        'tds_content.jsonl'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
        
    return True

def main():
    """Main entry point for the server"""
    try:
        # Check prerequisites
        if not check_prerequisites():
            sys.exit(1)
            
        # Create required directories
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Start the server
        logger.info("Starting production server...")
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            workers=1,  # Single worker for now since we have shared resources
            log_level="info",
            reload=False,
            access_log=True,
            timeout_keep_alive=65
        )
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
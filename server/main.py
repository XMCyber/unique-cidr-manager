"""
FastAPI CIDR Manager - Main Entry Point

This is the main entry point for the modernized CIDR Manager application.
It uses FastAPI with uvicorn for production-ready performance.
"""

import sys
import logging
from pathlib import Path

# Add the server directory to the Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

try:
    import uvicorn
    from config import get_settings, validate_environment
    
    logger = logging.getLogger(__name__)
    
    def main():
        """Main entry point for the application."""
        
        # Load settings (this will validate environment variables)
        try:
            settings = get_settings()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
        
        # Start the server
        logger.info("Starting CIDR Manager FastAPI server...")
        logger.info(f"Server will be available at: http://{settings.host}:{settings.port}")
        logger.info(f"API documentation will be available at: http://{settings.host}:{settings.port}/docs")
        logger.info(f"Alternative API docs at: http://{settings.host}:{settings.port}/redoc")
        
        uvicorn.run(
            "app:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True,
            server_header=False,  # Security: don't expose server info
            date_header=False     # Security: don't expose date info
        )
    
    if __name__ == '__main__':
        main()
        
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
    
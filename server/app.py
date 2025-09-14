"""
CIDR Manager Application
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
from pathlib import Path
from typing import Optional

from services import CIDRService, SubnetService
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CIDR Manager API",
    description="CIDR management system with backward-compatible API endpoints",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],  # Restricted to GET method
    allow_headers=["*"],
)

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
content_path = Path(__file__).parent.parent / "content"

app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Initialize services
cidr_service = CIDRService()
subnet_service = SubnetService()

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend():
    """Serve the main frontend HTML page."""
    try:
        html_file = frontend_path / "cidr.html"
        return FileResponse(html_file, media_type="text/html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend not found")

@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    """Serve favicon."""
    try:
        favicon_file = content_path / "favicon.ico"
        return FileResponse(favicon_file, media_type="image/x-icon")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Favicon not found")

@app.get("/cidr-manager.png", include_in_schema=False)
async def get_logo():
    """Serve logo image."""
    try:
        logo_file = content_path / "cidr-manager.png"
        return FileResponse(logo_file, media_type="image/png")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Logo not found")

# Serve static frontend files directly
@app.get("/style.css", include_in_schema=False)
async def get_style_css():
    """Serve CSS file."""
    try:
        css_file = frontend_path / "style.css"
        return FileResponse(css_file, media_type="text/css")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSS file not found")

@app.get("/cidr.js", include_in_schema=False)
async def get_cidr_js():
    """Serve CIDR JavaScript file."""
    try:
        js_file = frontend_path / "cidr.js"
        return FileResponse(js_file, media_type="text/javascript")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JavaScript file not found")

@app.get("/script.js", include_in_schema=False)
async def get_script_js():
    """Serve main JavaScript file."""
    try:
        js_file = frontend_path / "script.js"
        return FileResponse(js_file, media_type="text/javascript")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JavaScript file not found")

# Health check endpoint (new, non-breaking)
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "cidr-manager", "version": "3.0.0"}

# API endpoints
@app.get("/get-cidr", response_class=PlainTextResponse)
async def get_cidr(
    subnet_size: str = Query(..., description="Subnet size (e.g., 24 for /24)"),
    requiredrange: str = Query(..., description="Required range (10, 172, or 192)"),
    reason: str = Query(..., description="Reason for CIDR allocation")
):
    """
    Get a unique CIDR block and mark it as occupied.
    
    Endpoint - maintains exact same behavior as the previos version.
    """
    try:
        logger.info(f"Getting unique CIDR for reason: {reason}")
        result = cidr_service.get_unique_cidr(
            subnet_size=int(subnet_size),
            required_range=requiredrange,
            reason=reason
        )
        return str(result)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting unique CIDR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-next-cidr-no-push", response_class=PlainTextResponse)
async def get_next_cidr_no_push(
    subnet_size: str = Query(..., description="Subnet size (e.g., 24 for /24)"),
    requiredrange: str = Query(..., description="Required range (10, 172, or 192)"),
    reason: str = Query(..., description="Reason for checking")
):
    """
    Preview the next available CIDR block without allocating it.
    
    Original endpoint - maintains exact same behavior as the legacy system.
    """
    try:
        logger.info(f"Previewing next CIDR for reason: {reason}")
        result = cidr_service.get_next_cidr_no_push(
            subnet_size=int(subnet_size),
            required_range=requiredrange,
            reason=reason
        )
        return str(result)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error previewing CIDR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-occupied-list", response_class=PlainTextResponse)
async def get_occupied_list():
    """
    Get all occupied CIDR blocks.
    
    Original endpoint - returns JSON string exactly like the legacy system.
    """
    try:
        logger.info("Getting occupied CIDR list")
        result = cidr_service.get_all_occupied()
        return json.dumps(result, indent=4)
    except Exception as e:
        logger.error(f"Error getting occupied list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/delete-cidr-from-list", response_class=PlainTextResponse)
async def delete_cidr_from_list(
    cidr_deletion: str = Query(..., description="CIDR block to delete (e.g., 10.0.1.0/24)")
):
    """
    Delete a CIDR block from the occupied list.
    
    Original endpoint - maintains exact same behavior as the legacy system.
    """
    try:
        logger.info(f"Deleting CIDR: {cidr_deletion}")
        result = cidr_service.delete_cidr_from_list(cidr_deletion)
        return result
    except Exception as e:
        logger.error(f"Error deleting CIDR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/add-cidr-manually", response_class=PlainTextResponse)
async def add_cidr_manually(
    cidr: str = Query(..., description="CIDR block to add (e.g., 10.0.2.0/24)"),
    reason: str = Query(..., description="Reason for manual addition")
):
    """
    Manually add a CIDR block to the occupied list.
    
    Original endpoint - maintains exact same behavior as the legacy system.
    """
    try:
        logger.info(f"Manually adding CIDR: {cidr} for reason: {reason}")
        result = cidr_service.manually_add_cidr(cidr, reason)
        return result
    except Exception as e:
        logger.error(f"Error adding CIDR manually: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-subnets", response_class=PlainTextResponse)
async def get_subnets(
    subnet_size: str = Query(..., description="Target subnet size (e.g., 26 for /26)"),
    cidr: str = Query(..., description="Source CIDR block (e.g., 10.0.0.0/24)")
):
    """
    Calculate subnets from a given CIDR block.
    
    Original endpoint - returns space-separated subnets exactly like the legacy system.
    """
    try:
        logger.info(f"Getting subnets from CIDR: {cidr} with size: {subnet_size}")
        result = subnet_service.get_subnets_from_cidr(int(subnet_size), cidr)
        return " ".join(result)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting subnets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

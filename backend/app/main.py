"""
Socify SIEM Backend - Main Application
FastAPI application with local OpenSearch integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.ingest import router as ingest_router
from app.search import router as search_router
from app.alerts import router as alerts_router
from app.opensearch_client import test_connection
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Socify SIEM Backend",
    version="2.0.0",
    description="Cloud-native SIEM platform with Local OpenSearch",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(ingest_router, prefix="/api", tags=["Ingest"])
app.include_router(search_router, prefix="/api", tags=["Search"])
app.include_router(alerts_router, prefix="/api", tags=["Alerts"])
from app.rules_api import router as rules_router
app.include_router(rules_router, prefix="/api", tags=["Rules"])

# Register WebSocket routes
from app.websocket import router as websocket_router
app.include_router(websocket_router, tags=["WebSocket"])

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Socify SIEM Backend",
        "version": "2.0.0",
        "status": "operational",
        "storage": "Local OpenSearch"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for load balancers"""
    opensearch_status = test_connection()
    
    return {
        "status": "healthy" if opensearch_status["status"] == "connected" else "degraded",
        "service": "socify-backend",
        "checks": {
            "api": "ok",
            "opensearch": opensearch_status
        }
    }

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("Starting Socify SIEM Backend (Local OpenSearch)...")
    logger.info(f"OpenSearch Host: {os.getenv('OPENSEARCH_HOST', 'localhost')}:{os.getenv('OPENSEARCH_PORT', '9200')}")
    
    # Test OpenSearch connection
    connection_status = test_connection()
    if connection_status["status"] == "connected":
        logger.info(f"✓ Connected to OpenSearch {connection_status['version']}")
        logger.info(f"✓ Cluster: {connection_status['cluster_name']} (Health: {connection_status['cluster_health']})")
    else:
        logger.error(f"✗ OpenSearch connection failed: {connection_status.get('message')}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Shutting down Socify SIEM Backend...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

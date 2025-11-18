"""
FastAPI application main file
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import flights
from app.database import init_db

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Flight Management API",
    description="A RESTful API for managing flight data with CRUD operations, pagination, filtering, and sorting",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(flights.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "status": "success",
        "message": "Flight Management API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "success",
        "message": "Service is healthy"
    }


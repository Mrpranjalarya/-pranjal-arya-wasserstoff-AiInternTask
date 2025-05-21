# backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, query, document_routes
from app.db.session import engine, Base
import logging

# ---- Logging Setup ----
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

app = FastAPI(title="📄 Document Theme Chatbot API")

# ---- CORS Setup ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Automatically create database tables (if needed)
Base.metadata.create_all(bind=engine)

# ---- Middleware to log every request ----
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Completed request: {request.method} {request.url} -> {response.status_code}")
    return response

# Register all API routers
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(document_routes.router, prefix="/docs", tags=["Documents"])

@app.get("/")
def root():
    return {"message": "✅ Welcome to the Document Theme Chatbot API"}

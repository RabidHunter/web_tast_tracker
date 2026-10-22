import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict

from api.task_routes import router as task_router

app = FastAPI(title="Task Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response

app.add_middleware(RequestIdMiddleware)

RATE_LIMIT_WINDOW_MS = 10_000
MAX_REQUESTS = 8

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_store = defaultdict(lambda: {"count": 0, "ts": time.time() * 1000})

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        ip = request.client.host if request.client else "local"
        now = time.time() * 1000
        client_data = self.rate_store[ip]

        if now - client_data["ts"] < RATE_LIMIT_WINDOW_MS:
            client_data["count"] += 1
        else:
            client_data["count"] = 1
            client_data["ts"] = now

        if client_data["count"] > MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "too_many_requests", 
                    "code": 429, 
                    "details": "Rate limit exceeded",
                    "requestId": getattr(request.state, "request_id", "unknown")
                },
                headers={"Retry-After": "2"}
            )
            
        return await call_next(request)

app.add_middleware(RateLimitMiddleware)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": exc.status_code,
            "details": None,
            "requestId": getattr(request.state, "request_id", "unknown")
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "code": 422,
            "details": exc.errors(),
            "requestId": getattr(request.state, "request_id", "unknown")
        },
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(task_router)